from asyncio import sleep
import utils

import os 
import time
import socket
from dotenv import load_dotenv

import hikari
import songbird
from songbird import ytdl, ffmpeg
#from songbird.hikari import Voicebox


load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
bot = hikari.GatewayBot(ACCESS_TOKEN)


def bing(arg):
    print(arg.ssrc, arg.speaking)


@bot.listen()
async def ping(event: hikari.ShardReadyEvent) -> None:
    voice = await Voicebox.connect(bot, utils.GUILD_ID, utils.DEFAULT_CHANNEL_ID)
    await voice.add_event(songbird.Event.VoicePacket, bing)
    track_handle = await voice.play_source(await ffmpeg("/some/path/emotional_damage.mp3"))


bot.run()