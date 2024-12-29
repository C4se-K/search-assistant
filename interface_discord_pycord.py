import discord
from discord.ext import commands
import wave
import os
from dotenv import load_dotenv

import threading
import time

import numpy as np

#overrides
from discord.voice_client import VoiceClient
from discord.sinks import RecordingException, Sink
from discord.opus import DecodeManager, OpusError


"""
vars
"""


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

connections = {}


"""
basic fucntionalities ->
"""


@bot.event
async def on_ready():
    print("all systems nominal")
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










"""
audio capabilities
"""




#Overriding run from DecodeManager
#inspired from the following, under the MIT license
#https://github.com/Pycord-Development/pycord/blob/master/discord/opus.py#L521
class ExtendDecodeManager(DecodeManager):
    def run(self):
        print("start override decoder")
        print(self._end_thread.is_set())
        while not self._end_thread.is_set():
            #print(f'looping {len(self.decode_queue)}')
            try:
                data = self.decode_queue.pop(0)
            except IndexError:
                #print("error 1")
                time.sleep(0.001)
                continue
            print(f"looping {data}")
            try:
                if data.decrypted_data is None:
                    continue
                else:
                    print("got here")
                    data.decoded_data = self.get_decoder(data.ssrc).decode(data.decrypted_data)
            except OpusError:
                print("error occured while decoding opus")
                continue

            if data.decoded_data:
                print(f"{data.decoded_data.hex()}")

#Overriding start_recording from VoiceClient
#inspired from the following, under the MIT license
#https://github.com/Pycord-Development/pycord/blob/master/discord/voice_client.py#L52
class ExtendVoiceClient(VoiceClient):
    def start_recording(self, sink, callback, *args):
        #print("override complete")
        if not self.is_connected():
            raise RecordingException("Not connected to voice channel.")
        if not isinstance(sink, Sink):
            raise RecordingException("Must provide a Sink object.")
        #if not discord.opus.is_loaded():
           #discord.opus.load_opus('libopus.so')

        self.empty_socket()

        self.decoder = ExtendDecodeManager(self)
        self.decoder.start()

        self.recording = True
        self.decode_queue = []

        self.sink = sink
        sink.init(self)

        t = threading.Thread(
            target=self.recv_audio,
            args=(
                sink,
                callback,
                *args,
            ),
        )
        t.start()



async def once_done(_):
    pass

@bot.command()
async def join(ctx):
    """
    join the voice call the calling user is curently in

    then starts the recording stream
    
    """
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect(cls = ExtendVoiceClient)
        connections[ctx.guild.id] = vc
        await ctx.send(f"Connected to {channel.name}!")
    else:
        await ctx.send("You must be in a voice channel to use this command.")

    # start stream

    vc.start_recording(discord.sinks.WaveSink(), once_done)

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
    