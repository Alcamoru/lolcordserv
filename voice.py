import asyncio
from pprint import pprint

import discord
import requests.exceptions
import yt_dlp as youtube_dl
from yt_dlp import YoutubeDL
from discord.ext import commands
from googleapiclient.discovery import build
from requests import get

youtube_dl.utils.bug_reports_message = lambda: ""

with open("GOOGLE_TOKEN.txt", "r") as infile:
    GOOGLE_TOKEN = infile.read()

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": (
        "0.0.0.0"
    )
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


def search(arg):
    with YoutubeDL(ytdl_format_options) as ydl:
        try:
            get(arg)
        except requests.exceptions.MissingSchema or requests.exceptions.InvalidURL:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)
    return video


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source: discord.AudioSource, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        executable = r"C:\Users\alcam\OneDrive\Documents\Developpement\ffmpeg\ffmpeg-2023-06-21-git-1bcb8a7338-full_" \
                     r"build\bin\ffmpeg.exe"
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options,
                                          executable=executable),
                   data=data)


# noinspection PyTypeChecker,PyUnusedLocal
class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.connections = {}
        self.last_play = tuple()

    @commands.slash_command(name="play")
    async def play(self, ctx: discord.ApplicationContext, words):
        response: discord.InteractionResponse = ctx.response
        voice_client: discord.VoiceClient = ctx.voice_client
        await response.defer(ephemeral=False)

        # noinspection PyTypeChecker,PyUnusedLocal
        class MyView(discord.ui.View):

            def __init__(self):
                super().__init__()

            @discord.ui.button(label="Volume -", style=discord.ButtonStyle.primary, emoji="🔉")
            async def button_1_callback(self, button: discord.Button, interaction: discord.Interaction):
                voice_client.source.volume -= 0.1
                local_response: discord.InteractionResponse = interaction.response
                await local_response.edit_message(view=self)

            @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary, emoji="✅")
            async def button_pause(self, button: discord.Button, interaction: discord.Interaction):
                local_response: discord.InteractionResponse = interaction.response
                if not voice_client.is_paused():
                    voice_client.pause()
                    button.label = "Reprendre"
                    button.style = discord.ButtonStyle.success
                    await local_response.edit_message(view=self)
                else:
                    voice_client.resume()
                    button.label = "Pause"
                    button.style = discord.ButtonStyle.primary
                    await local_response.edit_message(view=self)

            @discord.ui.button(label="Volume +", style=discord.ButtonStyle.primary, emoji="🔊")
            async def button_3_callback(self, button: discord.Button, interaction: discord.Interaction):
                local_response: discord.InteractionResponse = interaction.response
                voice_client.source.volume += 0.1
                await local_response.edit_message(view=self)

        # noinspection PyTypeChecker
        video = search(words)
        url = video["original_url"]
        title = video["title"]

        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        voice_client.play(player, after=lambda e: print(f"Player error: {e}") if e else None)
        await ctx.respond(f"Playing: {player.title}", view=MyView())
        await self.is_last_played(ctx)
        self.last_play = (title, ctx)

    async def is_last_played(self, ctx):
        if self.last_play:
            if self.last_play[1].channel == ctx.channel:
                last_play_interaction: discord.Interaction = self.last_play[1].interaction
                embed = discord.Embed(title="Cette musique s'est terminée", description=f"{self.last_play[0]}")
                await last_play_interaction.edit_original_response(content="", embed=embed, view=None)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=self.bot.get_guild(1117482753076776982))
        if before.channel is None and after.channel is not None:
            voice_channel: discord.VoiceChannel = after.channel
            if not voice_client:
                await voice_channel.connect(reconnect=True)
                print(f"Le bot s'est connecté au canal vocal {voice_channel.name}")

        elif before.channel is not None and after.channel is None:
            channel: discord.VoiceChannel = before.channel
            if voice_client is not None and voice_client.channel == before.channel:
                if len(channel.members) <= 1:
                    await voice_client.disconnect(force=True)
                    print(f"Le bot s'est déconnecté du canal vocal {before.channel.name}")

    @play.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Vous n'êtes pas connectés à un channel vocal")
                raise commands.CommandError("Vous n'êtes pas connectés au channel vocal")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.slash_command(name="join")
    async def join(self, ctx: discord.ApplicationContext):
        # noinspection PyTypeChecker
        author: discord.Member = ctx.author
        voice_channel = author.voice.channel
        await voice_channel.connect()
        await ctx.respond("Connecté")

    @commands.slash_command(name="stop")
    async def stop(self, ctx: discord.ApplicationContext):
        await ctx.voice_client.disconnect(force=True)
        await ctx.respond("Déconnecté")
        await self.is_last_played(ctx)
        self.last_play = tuple()


def setup(bot: commands.Bot):
    bot.add_cog(Voice(bot))
