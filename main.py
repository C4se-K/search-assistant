from faster_whisper import WhisperModel
from scipy.signal import resample
from dotenv import load_dotenv
import numpy as np
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

from collections import deque
import numpy as np

import webrtcvad








vad = webrtcvad.Vad(2)

buffer = deque(maxlen=32000)
default_buffer_size = 16000
speech_active = False




"""

VAR setup

"""
start_time = time.time()

#general
raw_audio_queue = queue.Queue()
command_queue = queue.Queue()


#bot
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

#audio
target_sample_rate = 16000
target_channels = 1
target_bits_per_sample = 16

buffer = bytearray()
target_size = target_sample_rate * 2 #target sample rate is 16000 -> *2 = 32000,  2 seconds

print(f"[MAIN] general parameters took {(time.time() - start_time):.2f} seconds to start")

"""

faster-whisper model setup

"""
start_time = time.time()


#model parameters
model_size = "large-v3"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

model = WhisperModel(model_size, device="cuda", compute_type="float16")
print(f"[MAIN] faster-whisper took {(time.time() - start_time):.2f} seconds to start")

#ts = Transcription_Manger(raw_audio_queue)


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







audio_queue = queue.Queue()
transcription_list = []
buffer_count = 0
buffer_store = []

buffer = np.array([], dtype=np.int16)
target_size = 2 * 16000

l = 0

buffer_ready = False

print('[MAIN] all systems nominal')

revision_interval = 3
first_sentence = True

total = []
count = 0




def preprocess_decoded(data, original_sample_rate = 48000):
    #convert bytes to numpy array
    audio = np.frombuffer(data, dtype = np.int16)

    #convert to mono if stereo
    if len(audio) % 2 ==0:
        audio = audio.reshape(-1, 2)
        audio = np.mean(audio, axis = 1).astype(np.int16)
    else:
        raise ValueError("cannot interpret as stereo")
    
    #covert to 16000 hz
    if original_sample_rate != target_bits_per_sample:
        num_samples = int(len(audio) * (target_sample_rate / original_sample_rate))
        audio = resample(audio, num_samples).astype(np.int16)
    
    return audio

def process_audio(audio):
    start_time = time.time()
    #global buffer_count, buffer_store, total, first_sentence
    #$buffer_count += 1


    segments, _ = model.transcribe(audio, language="en", beam_size= 5)
    transcription = " ".join([segment.text for segment in segments])
    print(f"{(time.time() - start_time):.2f} sec: {transcription}")

    #if transcription.endswith(".") or transcription.endswith("?") or transcription.endswith("!"):
        #first_sentence = True




target_size = 16000
data_minimum = 1600
silence_threshold = 0.5
last_packet_time = time.time()

def process_buffer():
    global buffer, last_packet_time

    cur_time = time.time()

    if len(buffer) < target_size and len(buffer) >= data_minimum and (cur_time-last_packet_time) > silence_threshold:
        data_size = len(buffer)
        audio = np.frombuffer(buffer[:data_size], dtype=np.int16)

        #data = buffer[:target_size]
        buffer = buffer[data_size:]
        process_audio(audio)


    if len(buffer) >= target_size:
        #first_sentence = False
        audio = np.frombuffer(buffer[:target_size], dtype=np.int16)

        #data = buffer[:target_size]
        buffer = buffer[target_size:]
        process_audio(audio)



try:
    while True:
        if not command_queue.empty():
                print(command_queue.get()) 

        if not raw_audio_queue.empty():
            data = np.frombuffer(preprocess_decoded(raw_audio_queue.get()), dtype=np.int16)
            buffer = np.concatenate((buffer, np.frombuffer(data)))
            last_packet_time = time.time()

        #print(f"\r{len(buffer)}", end = " ")
        
        process_buffer()


        #time.sleep(0.05)
except KeyboardInterrupt:
    bot.leave_all()
finally:
    print("[MAIN] system terminated")


#if __name__ == "__main__":
    #main()
    