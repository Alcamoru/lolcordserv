import discord
from discord.ext import commands

from moderation import Moderation
from voice import Voice

intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description="Test description", intents=intents)

bot.load_extension("lolcommands")
bot.load_extension("moderation")
bot.load_extension("voice")


@bot.slash_command(name="test")
async def test(ctx):
    await ctx.respond("test")


@bot.event
async def on_ready():
    commands_channel: discord.TextChannel = bot.get_channel(1118494266482770030)
    ready_embed = discord.Embed(title="Statut du bot", description="Le bot est prêt")
    await commands_channel.send(embed=ready_embed)
    print("OK")

with open("DISCORD_TOKEN.txt", "r") as infile:
    DISCORD_TOKEN = infile.read()

bot.run(DISCORD_TOKEN)
