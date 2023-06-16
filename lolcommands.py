from datetime import datetime

import discord
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

        embed_profile = discord.Embed(title=f"Profil de {account_stats['name']}", description=account_stats["level"],
                                      type="rich")
        file = discord.File(f"media/ranked-emblem/emblem-{soloq_stats['tier']}.png", filename=f"emblem.png")
        embed_profile.set_author(name="Test", icon_url=f"attachment://emblem.png")
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


def setup(bot: commands.Bot):
    bot.add_cog(Lolbot(bot))
