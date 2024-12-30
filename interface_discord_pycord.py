from discord.ext import commands
from dotenv import load_dotenv
import numpy as np
import threading
import discord
import time
import wave
import os

from discord_audio_helper import ExtendVoiceClient

import threading
import queue
import asyncio

class Discord_Interface:
    def __init__(self, raw_audio_queue, command_queue, intents_msg=True, prefix = "!"):        
        """
        vars
        """
        #print("init")
        self.RAW_AUDIO = raw_audio_queue
        self.COMMAND = command_queue

        self.intents = discord.Intents.default()
        self.intents.message_content = intents_msg
        self.bot = commands.Bot(command_prefix=prefix, intents=self.intents)

        self.connections = {}

        self.register_basic_commands()
        self.register_audio_commands()

    def run_(self, ACCESS_TOKEN):
        self.bot.run(ACCESS_TOKEN)

    def enable_voice():
        pass

    def disable_voice():
        pass

    def register_basic_commands(self):
        
        """
        basic fucntionalities ->
        """

        @self.bot.event
        async def on_ready():
            self.COMMAND.put("all systems nominal")
            self.COMMAND.put(f"Bot is online as {self.bot.user}")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return

            self.COMMAND.put(f"Received message: {message.content}")
            await self.bot.process_commands(message)

        @self.bot.command()
        async def test(ctx):
            await ctx.send("Test command works!")

    def register_audio_commands(self):
        async def once_done(self, *args):
            pass #does nothing

        @self.bot.command()
        async def join(ctx):
            """
            join the voice call the calling user is curently in

            then starts the recording stream
            
            """
            #locates the sender and joins the call
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                vc = await channel.connect(cls = ExtendVoiceClient)
                self.connections[ctx.guild.id] = vc
                await ctx.send(f"Connected to {channel.name}!")
            else:
                await ctx.send("You must be in a voice channel to use this command.")

            # start stream
            vc.start_recording(discord.sinks.WaveSink(), once_done, raw_audio_queue= self.RAW_AUDIO)

        @self.bot.command()
        async def leave(ctx):
            #stop the websocket stream
            try:
                vc = self.connections[ctx.guild.id]
                vc.stop_recording()
            except Exception as e:
                print(f"caught an exception {e}")

            #leave the voice channel
            if ctx.guild.id in self.connections:
                vc = self.connections[ctx.guild.id]
                await vc.disconnect()
                del self.connections[ctx.guild.id]
                await ctx.send("Disconnected from the voice channel.")
            else:
                await ctx.send("Bot is not connected to a voice channel.")











