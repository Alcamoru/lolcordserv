import discord
from discord.ext import commands

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description="Test description", intents=intents)

bot.load_extension("lolcommands")
bot.load_extension("moderation")
bot.load_extension("voice")


@bot.event
async def on_ready():
    commands_channel: discord.TextChannel = bot.get_channel(1118494266482770030)
    ready_embed = discord.Embed(title="Statut du bot", description="Le bot est prêt")
    await commands_channel.send(embed=ready_embed)
    print("OK")


with open("DISCORD_TOKEN.txt", "r") as infile:
    DISCORD_TOKEN = infile.read()

bot.run(DISCORD_TOKEN)
