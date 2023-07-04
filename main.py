import discord
from discord.ext import commands

# Discord API Intents
intents = discord.Intents.all()

# Bot initialization and modules importation
# noinspection PyTypeChecker
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description="Test description", intents=intents)

bot.load_extension("lolcommands")
bot.load_extension("moderation")
bot.load_extension("voice")


# Called when the bot is online
@bot.event
async def on_ready():
    guild = bot.get_guild(1117482753076776982)
    moderation_channel: discord.TextChannel = guild.get_channel(1119542979896557600)
    ready_embed = discord.Embed(title="Statut du bot", description="Le bot est prêt",
                                color=discord.Color.from_rgb(51, 73, 255))
    await moderation_channel.send(embed=ready_embed)
    print("Bot pret")


# Called when an error happens
@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    error_embed: discord.Embed = discord.Embed(title="Erreur", description="Une erreur est survenue")
    if isinstance(error, commands.MissingRole):
        error_embed.add_field(name="Vous n'avez pas le role requis", value=str(error))
    elif isinstance(error, commands.CommandOnCooldown):
        error_embed.add_field(name="La commande est en attente", value=str(error))
    elif isinstance(error, commands.MissingRequiredArgument):
        error_embed.add_field(name="Il manque un argument", value=str(error))
    else:
        error_embed.add_field(name="Une erreur est survenue", value=str(error))


# Token importation
with open("DISCORD_TOKEN.txt", "r") as infile:
    DISCORD_TOKEN = infile.read()

bot.run(DISCORD_TOKEN)
