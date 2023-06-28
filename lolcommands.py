import json
from datetime import datetime
from pprint import pprint

import discord
import requests
from discord.commands import option
from discord.ext import commands
from riotwatcher import LolWatcher

with open("RIOT_TOKEN.txt", "r") as infile:
    RIOT_TOKEN = infile.read()

async def is_bot_channel(ctx: commands.Context):
    return ctx.channel.id == 1118494266482770030


def soloq_or_flex(summoner: list):
    if summoner[0]["queueType"] == "RANKED_SOLO_5x5":
        soloq: dict = summoner[0]
        flex: dict = summoner[1]
    else:
        soloq: dict = summoner[1]
        flex: dict = summoner[0]

    return soloq, flex


class Lolbot(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.watcher = LolWatcher(api_key=RIOT_TOKEN)
        self.region = "euw1"
        self.guild = self.bot.get_guild(1117482753076776982)

    def get_player_data(self, name, match):
        for player in match["info"]["participants"]:
            if player["summonerName"] == name:
                deaths = player["deaths"]
                kills = player["kills"]
                assists = player["assists"]
                champion = player["championName"]
                win = player["win"]
                team_id = player["teamId"]
                for team in match["info"]["teams"]:
                    if team["teamId"] == team_id:
                        all_kills = team["objectives"]["champion"]["kills"]
                kp = round(kills / all_kills * 100)
                return [deaths, kills, assists, champion, win, team_id, kp]


    @commands.has_role("LOLEUR")
    @commands.slash_command(name="profil", description="Profil du joueur")
    @option("invocateur", description="Entrez votre nom d'invocateur")
    async def profil(self, ctx: discord.ApplicationContext, invocateur):
        account = self.watcher.summoner.by_name(self.region, invocateur)
        summoner = self.watcher.league.by_summoner(self.region, account["id"])

        soloq, flex = soloq_or_flex(summoner)

        embed_profile = discord.Embed(title=f"{account['name']}", description=f'Niveau: {account["summonerLevel"]}',)
        file = discord.File(f"media/ranked-emblem/emblem-{soloq['tier']}.png", filename=f"emblem.png")

        embed_profile.set_author(name="Profil", icon_url=f"attachment://emblem.png")
        thumbnail_url = f"http://ddragon.leagueoflegends.com/cdn/13.11.1/img/profileicon/{account['profileIconId']}.png"
        embed_profile.set_thumbnail(url=thumbnail_url)
        embed_profile.add_field(name="Classé en solo/duo",
                                value=f":trophy:```{soloq['tier'].capitalize()} {soloq['rank']}```\n"
                                      f"{soloq['wins']} Victoires\n"
                                      f"{soloq['losses']} Défaites\n"
                                      f"{soloq['wins'] + soloq['losses']} Parties jouées\n ")
        embed_profile.add_field(name="Classé en flex",
                                value=f":trophy:```{flex['tier'].capitalize()} {flex['rank']}```\n"
                                      f"{flex['wins']} victoires\n"
                                      f"{flex['losses']} défaites\n"
                                      f"{flex['wins'] + flex['losses']} Parties jouées\n ")

        matchlist = self.watcher.match.matchlist_by_puuid(self.region, account["puuid"], count=3)
        matches = ""
        for match_id in matchlist[:3]:
            match = self.watcher.match.by_id(self.region, match_id)
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
            deaths, kills, assists, champion, win, team_id, kp = self.get_player_data(account["name"], match)
            matches += f"**Il y a {match_was} {date_unit}: -->** {champion}: {kills}/{deaths}/{assists}: " \
                       f"{'Victoire' if win else 'Défaite'}\n"
        embed_profile.add_field(name="Historique des matchs", value=matches, inline=False)
        await ctx.respond(embed=embed_profile, file=file)



    @commands.has_role("LOLEUR")
    @commands.slash_command(name="derniermatch", description="Dernier match du joueur")
    async def derniermatch(self, ctx: discord.ApplicationContext, invocateur):
        account = self.watcher.summoner.by_name(self.region, invocateur)
        last_match_id = self.watcher.match.matchlist_by_puuid(self.region, account["puuid"], count=1)[0]
        last_match = self.watcher.match.by_id(self.region, last_match_id)

        queue_id = last_match["info"]["queueId"]
        r = requests.get("https://static.developer.riotgames.com/docs/lol/queues.json")
        queues = json.loads(r.content)
        description = ""
        for queue in queues:
            if queue["queueId"] == queue_id:
                description = queue["description"].replace(" games", "")

        embed_last = discord.Embed(title="Alcamoru", description=description)

        deaths, kills, assists, champion, win, team_id, kp = self.get_player_data(account["name"], last_match)

        embed_last.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/{champion}.png")
        embed_last.add_field(name="KDA", value=f"{kills} kills, {deaths} deaths, {assists} assists")
        embed_last.add_field(name="Kill participation", value=f"{kp} % de participation aux éliminations", inline=False)
        blue_side_field = ""
        red_side_field = ""
        blue_side_kda = ""
        red_side_kda = ""
        blue_side_damages = ""
        red_side_damages = ""

        for team in last_match["info"]["teams"]:
            if team["teamId"] == 100 and team["win"] == True:
                blue_side_win = True
                red_side_win = False
            else:
                blue_side_win = False
                red_side_win = True

        for player in last_match["info"]["participants"]:
            deaths = player["deaths"]
            kills = player["kills"]
            assists = player["assists"]
            champion = player["championName"]
            win = player["win"]
            team_id = player["teamId"]
            role = player["teamPosition"]
            damages = player["totalDamageDealtToChampions"]
            if team_id == 100:
                blue_side_field += f"- ``{player['summonerName']}`` | {role}\n"
                blue_side_kda += f"- ``{kills}/{deaths}/{assists}`` : {round((kills + assists) / deaths, 2)} KDA\n"
                blue_side_damages += f"- ``{damages}``\n"
            if team_id == 200:
                red_side_field += f"- ``{player['summonerName']}`` | {role}\n"
                red_side_kda += f"- ``{kills}/{deaths}/{assists}`` : {round((kills + assists) / deaths, 2)} KDA\n"
                red_side_damages += f"- ``{damages}``\n"

        embed_last.add_field(name=f"Blue team ({'Victoire' if blue_side_win else 'Défaite'})", value=blue_side_field)
        embed_last.add_field(name="KDA", value=blue_side_kda)
        embed_last.add_field(name="Dégats", value=blue_side_damages)
        embed_last.add_field(name=f"Red team ({'Victoire' if red_side_win else 'Défaite'})", value=red_side_field)
        embed_last.add_field(name="KDA", value=red_side_kda)
        embed_last.add_field(name="Dégats", value=red_side_damages)

        await ctx.respond(embed=embed_last)


def setup(bot: commands.Bot):
    bot.add_cog(Lolbot(bot))
