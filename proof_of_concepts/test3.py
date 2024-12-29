import discord
from discord.ext import commands
import asyncio
import wave

import discord
import os
from dotenv import load_dotenv

class discord_interface:
    def __init__(self, ACCESS_TOKEN, PREFIX_ = "!"):
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.ACCESS_TOKEN_ = ACCESS_TOKEN

        self.bot = commands.Bot(command_prefix=PREFIX_, intents=self.intents)

        self.register_events()
        self.register_commands()

    def start(self):
        self.bot.run(self.ACCESS_TOKEN_)

    def register_events(self):
        @self.bot.event
        async def on_ready():
            print(f"Bot is online as {self.bot.user}")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return

            print(f"Received message: {message.content}")
            await self.bot.process_commands(message)

    def register_commands(self):
        @self.bot.command()
        async def test(ctx):
            await ctx.send("Test command works!")


if __name__ == "__main__":
    load_dotenv()
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    bot = discord_interface(ACCESS_TOKEN)
    bot.start()