import discord
from discord.ext import commands
import asyncio
import wave

import discord
import os
from dotenv import load_dotenv




import discord
from discord.ext import commands
import asyncio


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)



@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Received message: {message.content}")
    await bot.process_commands(message)

@bot.command()
async def test(ctx):
    await ctx.send("Test command works!")
















if __name__ == "__main__":
    load_dotenv()
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    bot.run(ACCESS_TOKEN)