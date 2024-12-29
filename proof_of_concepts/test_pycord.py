from enum import Enum
#https://guide.pycord.dev/voice/receiving
import discord

bot = discord.Bot(debug_guilds=[...])
connections = {}


class Sinks(Enum):
    mp3 = discord.sinks.MP3Sink(), "MP3 format audio recording"
    wav = discord.sinks.WaveSink(), "WAV format audio recording"
    pcm = discord.sinks.PCMSink(), "PCM format audio recording"
    ogg = discord.sinks.OGGSink(), "OGG format audio recording"
    mka = discord.sinks.MKASink(), "MKA format audio recording"
    mkv = discord.sinks.MKVSink(), "MKV format audio recording"
    mp4 = discord.sinks.MP4Sink(), "MP4 format audio recording"
    m4a = discord.sinks.M4ASink(), "M4A format audio recording"

    def __init__(self, sink, description):
        self.sink = sink
        self.description = description

    def __doc__(self):
        return self.description


async def finished_callback(sink, channel: discord.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()
    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]
    await channel.send(
        f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files
    )


@bot.command()
async def start(ctx: discord.ApplicationContext, sink: Sinks):
    """Record your voice!"""
    voice = ctx.author.voice

    if not voice:
        return await ctx.respond("You're not in a vc right now")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        sink.sink,
        finished_callback,
        ctx.channel,
    )

    await ctx.respond("The recording has started!")


@bot.command()
async def stop(ctx: discord.ApplicationContext):
    """Stop recording."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("Not recording in this guild.")


bot.run("TOKEN")