import discord
from discord.ext import commands

intents = discord.Intents.all()

# noinspection PyTypeChecker
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description="Test description", intents=intents)

bot.load_extension("lolcommands")
bot.load_extension("moderation")
bot.load_extension("voice")


@bot.event
async def on_ready():
    guild = bot.get_guild(1117482753076776982)
    moderation_channel: discord.TextChannel = guild.get_channel(1119542979896557600)
    ready_embed = discord.Embed(title="Statut du bot", description="Le bot est prêt",
                                color=discord.Color.from_rgb(51, 73, 255))
    await moderation_channel.send(embed=ready_embed)
    print("Bot pret")


with open("DISCORD_TOKEN.txt", "r") as infile:
    DISCORD_TOKEN = infile.read()

bot.run(DISCORD_TOKEN)
