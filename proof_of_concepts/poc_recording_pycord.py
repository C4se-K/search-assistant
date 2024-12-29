import discord
from discord.ext import commands
import wave
import os
from dotenv import load_dotenv


from threading import Event
import time



intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

connections = {}

#found on: 
#https://guide.pycord.dev/voice/receiving

# Join command
@bot.command()
async def join(ctx):
    """Command to make the bot join a voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()  # Connect to the voice channel the author is in.
        connections[ctx.guild.id] = vc  # Cache the connection.
        await ctx.send(f"Connected to {channel.name}!")
    else:
        await ctx.send("You must be in a voice channel to use this command.")

# Record command
@bot.command()
async def record(ctx):
    """Command to start recording audio."""
    if ctx.guild.id not in connections:
        await ctx.send("Bot is not connected to a voice channel.")
        return

    vc = connections[ctx.guild.id]
    vc.start_recording(
        discord.sinks.WaveSink(),  # Using WaveSink to record in WAV format.
        once_done,  # Callback function for when recording stops.
        ctx.channel  # Pass the text channel to send the result.
    )
    await ctx.send("Started recording!")

# Callback for when recording is done
async def once_done(sink: discord.sinks.WaveSink, channel: discord.TextChannel, *args):
    """Callback function called when the recording stops."""
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()  # Disconnect the bot from the voice channel.
    files = [
        discord.File(audio.file, f"{user_id}.{sink.encoding}")
        for user_id, audio in sink.audio_data.items()
    ]
    await channel.send(f"Finished recording audio for: {', '.join(recorded_users)}.", files=files)

# Stop recording command
@bot.command()
async def stop_recording(ctx):
    """Command to stop recording audio."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording and call the callback.
        del connections[ctx.guild.id]  # Remove from cache.
        await ctx.send("Stopped recording!")
    else:
        await ctx.send("I am not currently recording in this guild.")

# Leave command
@bot.command()
async def leave(ctx):
    """Command to make the bot leave the voice channel."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        await vc.disconnect()  # Disconnect the bot from the voice channel.
        del connections[ctx.guild.id]  # Remove from cache.
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("Bot is not connected to a voice channel.")






if __name__ == "__main__":
    load_dotenv()
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    bot.run(ACCESS_TOKEN)