import json
from datetime import datetime

import discord
import requests
from discord.commands import option
from discord.ext import commands
from riotwatcher import LolWatcher


async def is_bot_channel(ctx: commands.Context):
    return ctx.channel.id == 1118494266482770030


def soloq_or_flex(summoner: list):
    if summoner[0]["queueType"] == "RANKED_SOLO_5x5":
        soloq = summoner[0]
        flex = summoner[1]
    else:
        soloq = summoner[1]
        flex = summoner[0]
    return soloq, flex


class Lolbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("RIOT_TOKEN.txt", "r") as infile:
            RIOT_TOKEN = infile.read()
        self.watcher = LolWatcher(api_key=RIOT_TOKEN)
        self.region = "euw1"

    @commands.has_role("LOLEUR")
    @commands.slash_command(name="profil", description="Profil du joueur")
    @option("invocateur", description="Entrez votre nom d'invocateur")
    async def profil(self, ctx: discord.ApplicationContext, invocateur):
        account = self.watcher.summoner.by_name(self.region, invocateur)
        summoner = self.watcher.league.by_summoner(self.region, account["id"])
        soloq, flex = soloq_or_flex(summoner)
        account_stats = {"name": account["name"], "level": account["summonerLevel"], "iconId": account["profileIconId"]}
        soloq_stats = {"tier": soloq["tier"].lower(), "rank": soloq["rank"], "wins": soloq["wins"],
                       "losses": soloq["losses"]}
        flex_stats = {"tier": flex["tier"].lower(), "rank": flex["rank"], "wins": flex["wins"],
                      "losses": flex["losses"]}

        embed_profile = discord.Embed(title=f"{account_stats['name']}", description=f'Niveau: {account_stats["level"]}',
                                      type="rich")
        file = discord.File(f"media/ranked-emblem/emblem-{soloq_stats['tier']}.png", filename=f"emblem.png")
        embed_profile.set_author(name="Profil", icon_url=f"attachment://emblem.png")
        embed_profile.set_thumbnail(
            url=f"http://ddragon.leagueoflegends.com/cdn/13.11.1/img/profileicon/{account_stats['iconId']}.png")
        embed_profile.add_field(name="Classé en solo/duo",
                                value=f":trophy:```{soloq_stats['tier'].capitalize()} {soloq_stats['rank']}```\n"
                                      f"{soloq_stats['wins']} Victoires\n"
                                      f"{soloq_stats['losses']} Défaites\n"
                                      f"{soloq_stats['wins'] + soloq_stats['losses']} Parties jouées\n ")
        embed_profile.add_field(name="Classé en flex",
                                value=f":trophy:```{flex_stats['tier'].capitalize()} {flex_stats['rank']}```\n"
                                      f"{flex_stats['wins']} victoires\n"
                                      f"{flex_stats['losses']} défaites\n"
                                      f"{flex_stats['wins'] + flex_stats['losses']} Parties jouées\n ")
        matches = self.watcher.match.matchlist_by_puuid(self.region, account["puuid"], count=3)
        value = ""
        for i in range(3):
            match = self.watcher.match.by_id(self.region, matches[i])
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

            deaths = ""
            kills = ""
            assists = ""
            champion = ""
            win = ""
            for player in match["info"]["participants"]:
                if player["summonerName"] == account_stats["name"]:
                    deaths = player["deaths"]
                    kills = player["kills"]
                    assists = player["assists"]
                    champion = player["championName"]
                    win = player["win"]
            value += f"**Il y a {match_was} {date_unit}: -->** {champion}: {kills}/{deaths}/{assists}: " \
                     f"{'Victoire' if win else 'Défaite'}\n"
        embed_profile.add_field(name="Historique des matchs", value=value, inline=False)
        await ctx.respond(embed=embed_profile, file=file)

    @commands.has_role("LOLEUR")
    @commands.slash_command(name="derniermatch", description="Dernier match du joueur")
    async def derniermatch(self, ctx: discord.ApplicationContext, invocateur):
        account = self.watcher.summoner.by_name(self.region, invocateur)
        print(account["puuid"])
        summoner = self.watcher.league.by_summoner(self.region, account["id"])
        account_stats = {"name": account["name"], "level": account["summonerLevel"], "iconId": account["profileIconId"]}
        last_match = self.watcher.match.matchlist_by_puuid(self.region, account["puuid"], count=1)[0]
        match = self.watcher.match.by_id(self.region, last_match)
        queue_id = match["info"]["queueId"]
        r = requests.get("https://static.developer.riotgames.com/docs/lol/queues.json")
        queues = json.loads(r.content)
        for queue in queues:
            if queue["queueId"] == queue_id:
                description = queue["description"].replace(" games", "")
        embed_last = discord.Embed(title="Alcamoru", description=description)
        blue_team = dict()
        red_team = dict()
        for player in match["info"]["participants"]:
            if player["teamId"] == 100:
                blue_team[player["summonerName"]] = player["teamPosition"]
                blue_team_win = player["win"]
            elif player["teamId"] == 200:
                red_team[player["summonerName"]] = player["teamPosition"]
            if player["summonerName"] == account_stats["name"]:
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
        embed_last.add_field(name="KDA", value=f"{kills} kills, {deaths} deaths, {assists} assists")
        embed_last.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/{champion}.png")
        embed_last.add_field(name="Kill participation", value=f"{kp} % de participation aux éliminations", inline=False)
        field = ""
        for key, value in blue_team.items():
            if value == "TOP":
                value = "Top"
            if value == "JUNGLE":
                value = "Jungle"
            if value == "MIDDLE":
                value = "Mid"
            if value == "BOTTOM":
                value = "ADC"
            if value == "UTILITY":
                value = "Support"
            field += f"- ``{key}`` | {value}\n"
        embed_last.add_field(name=f"Blue team ({'Victoire' if blue_team_win else 'Défaite'})", value=field)
        field = ""
        field_kda = ""
        field_damages = ""
        for player in match["info"]["participants"][0:5]:
            deaths = player["deaths"]
            kills = player["kills"]
            assists = player["assists"]
            damages = player["totalDamageDealtToChampions"]
            field_damages += f"- ``{damages}``\n"
            field_kda += f"- ``{kills}/{deaths}/{assists}`` : {round((kills + assists) / deaths, 2)} KDA\n"
        embed_last.add_field(name="KDA", value=field_kda)
        embed_last.add_field(name="Dégats", value=field_damages)
        await ctx.respond(embed=embed_last)

        for key, value in red_team.items():
            if value == "TOP":
                value = "Top"
            if value == "JUNGLE":
                value = "Jungle"
            if value == "MIDDLE":
                value = "Mid"
            if value == "BOTTOM":
                value = "ADC"
            if value == "UTILITY":
                value = "Support"
            field += f"- ``{key}`` | {value}\n"
        embed_last.add_field(name=f"Red team ({'Victoire' if not blue_team_win else 'Défaite'})", value=field)
        field_kda = ""
        field_damages = ""
        for player in match["info"]["participants"][5:]:
            deaths = player["deaths"]
            kills = player["kills"]
            assists = player["assists"]
            damages = player["totalDamageDealtToChampions"]
            field_damages += f"- ``{damages}``\n"
            field_kda += f"- ``{kills}/{deaths}/{assists}`` : {round((kills + assists) / deaths, 2)} KDA\n"
        embed_last.add_field(name="KDA", value=field_kda)
        embed_last.add_field(name="Dégats", value=field_damages)
        await ctx.respond(embed=embed_last)


def setup(bot: commands.Bot):
    bot.add_cog(Lolbot(bot))
