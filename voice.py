from enum import Enum

import discord
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.connections = {}

    class Sinks(Enum):
        mp3 = discord.sinks.MP3Sink()
        wav = discord.sinks.WaveSink()
        pcm = discord.sinks.PCMSink()
        ogg = discord.sinks.OGGSink()
        mka = discord.sinks.MKASink()
        mkv = discord.sinks.MKVSink()
        mp4 = discord.sinks.MP4Sink()
        m4a = discord.sinks.M4ASink()

    async def finished_callback(self, sink, channel: discord.TextChannel, *args):
        recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
        await sink.vc.disconnect()
        files = [
            discord.File(audio.file, f"{user_id}.{sink.encoding}")
            for user_id, audio in sink.audio_data.items()
        ]
        await channel.send(
            f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
        )

    @commands.command()
    async def start(self, ctx: discord.ApplicationContext, sink: Sinks):
        """Record your voice!"""
        voice = ctx.author.voice

        if not voice:
            return await ctx.respond("You're not in a vc right now")

        vc = await voice.channel.connect()
        self.connections.update({ctx.guild.id: vc})

        vc.start_recording(
            sink.value,
            self.finished_callback,
            ctx.channel,
        )

        await ctx.respond("The recording has started!")

    @commands.command()
    async def stop(self, ctx: discord.ApplicationContext):
        """Stop recording."""
        if ctx.guild.id in self.connections:
            vc = self.connections[ctx.guild.id]
            vc.stop_recording()
            del self.connections[ctx.guild.id]
            await ctx.delete()
        else:
            await ctx.respond("Not recording in this guild.")
