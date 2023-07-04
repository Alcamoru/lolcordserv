import asyncio

import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from youtubesearchpython import VideosSearch

youtube_dl.utils.bug_reports_message = lambda: ""

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
    ),
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


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


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.connections = {}

    @commands.slash_command(name="play")
    async def play(self, ctx: commands.Context, words):
        vs = VideosSearch(words, limit=1, region="EU")
        # noinspection PyTypeChecker
        url = vs.result()["result"][0]["link"]
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Playing: {player.title}")

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
                raise commands.CommandError("Author not connected to a voice channel.")
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


def setup(bot: commands.Bot):
    bot.add_cog(Voice(bot))
