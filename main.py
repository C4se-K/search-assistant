from faster_whisper import WhisperModel
from scipy.signal import resample
from dotenv import load_dotenv
from collections import deque
import numpy as np
import webrtcvad
import threading
import asyncio
import socket
import queue
import time
import math
import wave
import os 

from interface_discord_pycord import Discord_Interface
from transcription import Transcription_Manager



"""

VAR setup

"""
start_time = time.time()

#general
raw_audio_queue = queue.Queue()
command_queue = queue.Queue()
audio_queue = queue.Queue()

#bot
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
print(f"[MAIN] general parameters took {(time.time() - start_time):.2f} seconds to start")


"""

discord bot setup

"""
start_time = time.time()
#interface discord bot
bot_ready = threading.Event()
bot = Discord_Interface(raw_audio_queue, command_queue, bot_ready)
threading.Thread(target=bot.run_, args = (ACCESS_TOKEN,), daemon=True).start()

#wait for bot to start
bot_ready.wait()
print(f"[MAIN] discord interface bot took {(time.time() - start_time):.2f} seconds to start")
start_time = time.time()


#transcription_list = []

send = queue.Queue()

start_time = time.time()
transcription  = Transcription_Manager(send)
print(f"[MAIN] Transcription Manager took {(time.time() - start_time):.2f} seconds to start")


def messenger():
    while True:
        if not command_queue.empty():
            print(command_queue.get()) 

        if not send.empty():
            bot.send_message(send.get())

        if not raw_audio_queue.empty():
            transcription.add_to_buffer(raw_audio_queue.get())

ms = threading.Thread(target = messenger, daemon=True).start()



print('[MAIN] all systems nominal')


try:
    
    while True:
        #print(f"\r{len(buffer)}", end = " ")
        #being called too early

        transcription.process_buffer()
        time.sleep(0.1)

except KeyboardInterrupt:
    bot.leave_all()
finally:
    print("[MAIN] system terminated")


#if __name__ == "__main__":
    #main()
    