import discord
from discord.ext import commands
import wave
import os
from dotenv import load_dotenv
#from .opus import Encoder


from threading import Event
import time

#overrides
from discord.voice_client import VoiceClient
from discord.opus import DecodeManager, OpusError


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

connections = {}


#inspired from the following, under the MIT license
#https://github.com/Pycord-Development/pycord/blob/master/discord/opus.py#L521
class ExtendDecodeManager(DecodeManager):
    def run(self):
        while not self._end_thread.is_set():
            try:
                data = self.decode_queue.pop(0)
            except IndexError:
                time.sleep(0.001)
                continue

            try:
                if data.decrypted_data is None:
                    continue
                else:
                    data.decoded_data = self.get_decoder(data.ssrc).decode(data.decrypted_data)
            except OpusError:
                continue


#inspired from the following, under the MIT license
#https://github.com/Pycord-Development/pycord/blob/master/discord/voice_client.py#L52
class ExtendVoiceClient(VoiceClient):
    def start_recording(self):
        print("override complete")


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

    vc.start_recording()






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