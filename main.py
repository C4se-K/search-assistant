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









def process_opus_decoded():
    pass

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

def transcribe(audio):
    #print(len(audio))
    """
    if len(audio) != 32000:
        raise ValueError("incorrect len")
    if len(audio.shape) != 1:
        raise ValueError("incorrect shape")
    """
    #print(f"test: sample size: {len(audio)}")

    #audio = audio.astype(np.float32) / 32768.0

    segments, _ = model.transcribe(audio, beam_size=4)

    transcription = []
    for segment in segments:
       # transcription.append(segment["text"])
       print(segment.text)

    #print(transcription)
    #return transcription

def handle_stream(length= 2):
    ...











def main():
    print('[MAIN] all systems nominal')
    try:
        while True:
            if not command_queue.empty():
                print(command_queue.get())   

            if not raw_audio_queue.empty():
                data = raw_audio_queue.get()
                buffer.extend(preprocess_decoded(data))


            if len(buffer) >= target_size:
                audio = np.frombuffer(buffer[:target_size], dtype=np.int16)
                audio = audio.astype(np.float32) / 32768.0
                transcribe(audio)

                buffer = buffer[target_size:]
                

            #time.sleep(0.1)
    except KeyboardInterrupt:
        ...

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

#model parameters
model_size = "large-v3"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"



"""

faster-whisper model setup

"""

model = WhisperModel(model_size, device="cuda", compute_type="float16")
print(f"[MAIN] faster-whisper took {(time.time() - start_time):.2f} seconds to start")
start_time = time.time()

#ts = Transcription_Manger(raw_audio_queue)


"""

discord bot setup

"""
#interface discord bot
bot_ready = threading.Event()

bot = Discord_Interface(raw_audio_queue, command_queue, bot_ready)
threading.Thread(target=bot.run_, args = (ACCESS_TOKEN,), daemon=True).start()

#wait for bot to start
bot_ready.wait()
print(f"[MAIN] discord interface bot took {(time.time() - start_time):.2f} seconds to start")
start_time = time.time()




if __name__ == "__main__":
    main()
    