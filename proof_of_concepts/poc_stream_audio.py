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


"""

Basic functions: join and leave


"""


class Opus_decoder:
    def __init__(self):
        pass

    def run():
        pass

    def decode():
        pass


@bot.command()
async def join(ctx):
    """
    join the voice call the calling user is curently in

    then starts the recording stream
    
    """
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        connections[ctx.guild.id] = vc
        await ctx.send(f"Connected to {channel.name}!")
    else:
        await ctx.send("You must be in a voice channel to use this command.")

    # start stream








@bot.command()
async def leave(ctx):
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