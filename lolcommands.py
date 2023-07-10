import json
from datetime import datetime
from typing import TextIO

import discord
import requests
from discord.commands import SlashCommandGroup
from discord.commands import option
from discord.ext import commands
from riotwatcher import LolWatcher


# Tokens importation
infile: TextIO
with open("RIOT_TOKEN.txt", "r") as infile:
    RIOT_TOKEN = infile.read()


# Select the queue types (Soloq or Flex)
def soloq_or_flex(summoner: list) -> tuple:
    """

    :type summoner: list
    :rtype: tuple
    """
    if summoner[0]["queueType"] == "RANKED_SOLO_5x5":
        soloq: dict = summoner[0]
        flex: dict = summoner[1]
    else:
        soloq: dict = summoner[1]
        flex: dict = summoner[0]

    return soloq, flex


# Main class for commands
# noinspection PyTypeChecker
class Lolbot(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.watcher = LolWatcher(api_key=RIOT_TOKEN)
        self.region = "euw1"
        self.guild: discord.Guild = self.bot.get_guild(1117482753076776982)

    stats = SlashCommandGroup(name="stats", description="Les commandes relatives aux statistiques du jeu")

    # A command to get the user's profile
    @commands.has_role("LOLEUR")
    @commands.slash_command(name="profil", description="Profil du joueur")
    @commands.cooldown(1, 20, commands.BucketType.user)
    @option(name="invocateur", description="Entrez votre nom d'invocateur")
    async def profil(self, ctx: discord.ApplicationContext, invocateur):
        try:
            account = self.watcher.summoner.by_name(self.region, invocateur)
            response: discord.InteractionResponse = ctx.response
            await response.defer(ephemeral=False)
            # Get user information
            summoner = self.watcher.league.by_summoner(self.region, account["id"])

            soloq, flex = soloq_or_flex(summoner)

            # Embed creation
            embed = discord.Embed(title=f"{account['name']}", description=f'Niveau: {account["summonerLevel"]}',
                                  color=discord.Color.from_rgb(35, 209, 80))
            # We get rank emblem from static media
            file = discord.File(f"media/ranked-emblem/emblem-{soloq['tier']}.png", filename=f"emblem.png")

            embed.set_author(name="Profil", icon_url=f"attachment://emblem.png")
            thumbnail_url = \
                f"http://ddragon.leagueoflegends.com/cdn/13.11.1/img/profileicon/{account['profileIconId']}.png"
            embed.set_thumbnail(url=thumbnail_url)
            embed.add_field(name="Classé en solo/duo",
                            value=f":trophy:```{soloq['tier'].capitalize()} {soloq['rank']}```\n"
                                  f"{soloq['wins']} Victoires\n"
                                  f"{soloq['losses']} Défaites\n"
                                  f"{soloq['wins'] + soloq['losses']} Parties jouées\n ")
            embed.add_field(name="Classé en flex",
                            value=f":trophy:```{flex['tier'].capitalize()} {flex['rank']}```\n"
                                  f"{flex['wins']} victoires\n"
                                  f"{flex['losses']} défaites\n"
                                  f"{flex['wins'] + flex['losses']} Parties jouées\n ")

            match_list = self.watcher.match.matchlist_by_puuid(self.region, account["puuid"], count=3)
            matches = ""
            # Last 3 matches from the match list
            for match_id in match_list[:3]:
                match: dict = self.watcher.match.by_id(self.region, match_id)

                # Calculation of when was the match
                date = datetime.fromtimestamp(int(str(match["info"]["gameStartTimestamp"])[:-3]))
                now = datetime.now()
                match_was = now - date
                match_was = round(match_was.total_seconds() / 3600)

                if match_was >= 24:
                    match_was = round(match_was / 24)
                    date_unit = "jours"
                else:
                    if match_was == 1:
                        date_unit = "heure"
                    else:
                        date_unit = "heures"

                for player in match["info"]["participants"]:
                    if player["summonerName"] == account["name"]:
                        win = player["win"]
                        matches += f"**Il y a {match_was} {date_unit}: -->** {player['championName']}:" \
                                   f" {player['kills']}/{player['deaths']}/{player['assists']}: " \
                                   f"{'Victoire' if win else 'Défaite'}\n"
            embed.add_field(name="Historique des matchs", value=matches, inline=False)
        except requests.exceptions.HTTPError:
            embed = discord.Embed(title="Erreur", description="Une erreur est survenue", color=discord.Color.red())
            embed.add_field(name="L'invocateur est introuvable",
                            value="Veuillez entrer un nom d'invocateur valide")
            file = None
        await ctx.respond(embed=embed, file=file, ephemeral=False)

    # A command to get user's last match information
    @commands.has_role("LOLEUR")
    @commands.slash_command(name="derniermatch", description="Dernier match du joueur")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def derniermatch(self, ctx: discord.ApplicationContext, invocateur):

        try:
            response: discord.InteractionResponse = ctx.response
            await response.defer(ephemeral=False)
            # User information
            account = self.watcher.summoner.by_name(self.region, invocateur)
            last_match_id: str = self.watcher.match.matchlist_by_puuid(self.region, account["puuid"], count=1)[0]
            last_match = self.watcher.match.by_id(self.region, last_match_id)

            # Getting the queue type from data dragon
            queue_id = last_match["info"]["queueId"]
            r = requests.get("https://static.developer.riotgames.com/docs/lol/queues.json")
            queues = json.loads(r.content)
            description = ""
            for queue in queues:
                if queue["queueId"] == queue_id:
                    description = queue["description"].replace(" games", "")

            # Retrieve player data
            player, win, kp = None, None, None
            for participant in last_match["info"]["participants"]:
                if str(participant["summonerName"]) == invocateur:
                    player = participant
                    win = participant["win"]
                    for team in last_match["info"]["teams"]:
                        if team["teamId"] == participant["teamId"]:
                            kp = round(participant["kills"] / team["objectives"]["champion"]["kills"] * 100)

            if win:
                color = discord.Color.from_rgb(36, 218, 71)
            else:
                color = discord.Color.from_rgb(218, 36, 36)

            # Embed creation
            embed = discord.Embed(title=f"{invocateur}", description=description,
                                  color=color)

            thumbnail_url = f"http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/{player['championName']}.png"
            embed.set_thumbnail(url=thumbnail_url)
            embed.add_field(name="KDA", value=f"{player['kills']} kills, {player['deaths']} deaths, "
                                              f"{player['assists']} assists")
            embed.add_field(name="Kill participation", value=f"{kp} % de participation aux éliminations", inline=False)
            blue_side_field = ""
            red_side_field = ""
            blue_side_kda = ""
            red_side_kda = ""
            blue_side_damages = ""
            red_side_damages = ""

            blue_side_win = None
            red_side_win = None

            for team in last_match["info"]["teams"]:
                if int(team["teamId"]) == 100 and bool(team["win"]):
                    blue_side_win = True
                    red_side_win = False
                else:
                    blue_side_win = False
                    red_side_win = True

            for player in last_match["info"]["participants"]:
                deaths = int(player["deaths"])
                kills = int(player["kills"])
                assists = int(player["assists"])
                role = player["teamPosition"]
                damages = int(player["totalDamageDealtToChampions"])
                if int(player["teamId"]) == 100:
                    blue_side_field += f"- ``{player['summonerName']}`` | {role}\n"
                    blue_side_kda += f"- ``{kills}/{deaths}/{assists}`` : {round((kills + assists) / deaths, 2)} KDA\n"
                    blue_side_damages += f"- ``{damages}``\n"
                if int(player["teamId"]) == 200:
                    red_side_field += f"- ``{player['summonerName']}`` | {role}\n"
                    red_side_kda += f"- ``{kills}/{deaths}/{assists}`` : {round((kills + assists) / deaths, 2)} KDA\n"
                    red_side_damages += f"- ``{damages}``\n"

            embed.add_field(name=f"Blue team ({'Victoire' if blue_side_win else 'Défaite'})", value=blue_side_field)
            embed.add_field(name="KDA", value=blue_side_kda)
            embed.add_field(name="Dégats", value=blue_side_damages)
            embed.add_field(name=f"Red team ({'Victoire' if red_side_win else 'Défaite'})", value=red_side_field)
            embed.add_field(name="KDA", value=red_side_kda)
            embed.add_field(name="Dégats", value=red_side_damages)

        except requests.exceptions.HTTPError:
            embed = discord.Embed(title="Erreur", description="Une erreur est survenue", color=discord.Color.red())
            embed.add_field(name="L'invocateur est introuvable",
                            value="Veuillez entrer un nom d'invocateur valide")
        await ctx.respond(embed=embed, ephemeral=False)


def setup(bot: commands.Bot):
    bot.add_cog(Lolbot(bot))
