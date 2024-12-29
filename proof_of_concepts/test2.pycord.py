import discord
from discord.ext import commands
import asyncio
import wave

import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)



@bot.command()
async def test(ctx):
    await ctx.send("Test command works!")

class AudioRecorder:
    def __init__(self):
        self.audio_data = []

    def record_audio(self, pcm_data):
        """Stores raw PCM data from the audio stream."""
        self.audio_data.append(pcm_data)

    def save_audio(self, filename="output.wav"):
        """Saves the recorded audio to a WAV file."""
        with wave.open(filename, "wb") as wf:
            # Define WAV file properties (16-bit PCM, 48kHz, mono)
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(b"".join(self.audio_data))

@bot.command()
async def join(ctx):
    print(ctx.author)
    """Command to make the bot join a voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        print(f"Connected to {channel.name}.")
    else:
        await ctx.send("You must be in a voice channel to use this command.")

@bot.command()
async def record(ctx, duration: int = 10):
    """Command to record audio from the voice channel."""
    vc = ctx.guild.voice_client
    if vc and vc.is_connected():
        if not vc.is_listening():
            recorder = AudioRecorder()

            def callback(pcm_data, user):
                """Callback function for audio stream."""
                if pcm_data:  # Only record if data is present
                    recorder.record_audio(pcm_data)

            # Start listening to the audio stream
            vc.listen(discord.AudioSink(callback=callback))
            await ctx.send(f"Recording audio for {duration} seconds...")

            # Wait for the specified duration
            await asyncio.sleep(duration)

            # Stop listening and save the audio
            vc.stop_listening()
            recorder.save_audio("recorded_audio.wav")
            await ctx.send("Recording saved as 'recorded_audio.wav'.")
        else:
            await ctx.send("Already recording!")
    else:
        await ctx.send("Bot is not connected to a voice channel.")

@bot.command()
async def leave(ctx):
    """Command to make the bot leave the voice channel."""
    vc = ctx.guild.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("Bot is not connected to a voice channel.")

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
bot.run(ACCESS_TOKEN)