import discord
import os
from dotenv import load_dotenv

bot = discord.Bot()
connections = {}

class AudioListener(discord.AudioSink):
    def __init__(self):
        self.running = True

    def write(self, data):
        if self.running:
            print("Receiving audio...")

@bot.command()
async def join(ctx):
    """Joins the caller's voice channel and starts receiving audio."""
    voice = ctx.author.voice

    if not voice:
        await ctx.respond("You aren't in a voice channel!")
        return

    vc = await voice.channel.connect()  # Connect to the caller's voice channel
    connections[ctx.guild.id] = vc  # Cache the connection

    listener = AudioListener()  # Create an audio listener
    vc.listen(listener)  # Start receiving audio with the listener

    await ctx.respond("Joined the channel and started receiving audio.")

@bot.command()
async def leave(ctx):
    """Leaves the voice channel and stops receiving audio."""
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_listening()  # Stop receiving audio
        await vc.disconnect()  # Disconnect from the voice channel
        del connections[ctx.guild.id]  # Remove the connection from the cache
        await ctx.respond("Left the voice channel and stopped receiving audio.")
    else:
        await ctx.respond("I am not in a voice channel.")

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
bot.run(ACCESS_TOKEN)
