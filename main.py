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
#from transcription import Transcription_Manager

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









class Transcription_Manager:
    def __init__(self): # , ready <- assuming this is threaded
        #self.READY = ready

        #audio
        self.target_sample_rate = 16000
        self.target_channels = 1
        self.target_bits_per_sample = 16

        self.target_size = 16000 # variable to change
        self.data_minimum = 1600
        self.silence_threshold = 0.5
        self.last_packet_time = time.time()

        self.buffer = np.array([], dtype=np.int16)

        
        self.model_size = "large-v3"
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        self.model = None


        self.revision_interval = 3
        self.first_sentence = True


        self.intiaite_model()

        self.on_ready()

    def on_ready(self):
        #self.READY.set()
        pass

    """
        faster-whisper model setup
    """
    def intiaite_model(self):
        start_time = time.time()
        #model parameters
        
        self.model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
        print(f"[MAIN] faster-whisper took {(time.time() - start_time):.2f} seconds to start")

    def add_to_buffer(self, data): #raw_audio_queue.get()
        #print('being called')
        temp = np.frombuffer(self.preprocess_decoded(data), dtype=np.int16)
        self.buffer = np.concatenate((self.buffer, np.frombuffer(temp)))
        self.last_packet_time = time.time()
        #print(len(self.buffer))

    def preprocess_decoded(self, data, original_sample_rate = 48000):
        #convert bytes to numpy array
        audio = np.frombuffer(data, dtype = np.int16)

        #convert to mono if stereo
        if len(audio) % 2 ==0:
            audio = audio.reshape(-1, 2)
            audio = np.mean(audio, axis = 1).astype(np.int16)
        else:
            raise ValueError("cannot interpret as stereo")
        
        #covert to 16000 hz
        if original_sample_rate != self.target_bits_per_sample:
            num_samples = int(len(audio) * (self.target_sample_rate / original_sample_rate))
            audio = resample(audio, num_samples).astype(np.int16)
        
        return audio

    def process_audio(self, audio):
        start_time = time.time()
        #global buffer_count, buffer_store, total, first_sentence
        #$buffer_count += 1


        segments, _ = self.model.transcribe(audio, language="en", beam_size= 5)
        transcription = " ".join([segment.text for segment in segments])
        print(f"{(time.time() - start_time):.2f} sec: {transcription}")

        #if transcription.endswith(".") or transcription.endswith("?") or transcription.endswith("!"):
            #first_sentence = True

    def process_buffer(self):
        #print('being called 2')

        cur_time = time.time()

        if (len(self.buffer) < self.target_size and 
            len(self.buffer) >= self.data_minimum and 
            (cur_time-self.last_packet_time) > self.silence_threshold):

            data_size = len(self.buffer)
            audio = np.frombuffer(self.buffer[:data_size], dtype=np.int16)

            #data = buffer[:target_size]
            self.buffer = self.buffer[data_size:]
            self.process_audio(audio)


        if len(self.buffer) >= self.target_size:
            #first_sentence = False
            audio = np.frombuffer(self.buffer[:self.target_size], dtype=np.int16)

            #data = buffer[:target_size]
            self.buffer = self.buffer[self.target_size:]
            self.process_audio(audio)


    


audio_queue = queue.Queue()
#transcription_list = []


start_time = time.time()
transcription  = Transcription_Manager()
print(f"[MAIN] Transcription Manager took {(time.time() - start_time):.2f} seconds to start")


print('[MAIN] all systems nominal')
try:
    
    while True:
        if not command_queue.empty():
                print(command_queue.get()) 

        if not raw_audio_queue.empty():
            transcription.add_to_buffer(raw_audio_queue.get())

            #data = np.frombuffer(transcription.preprocess_decoded(raw_audio_queue.get()), dtype=np.int16)
            #buffer = np.concatenate((buffer, np.frombuffer(data)))
            #last_packet_time = time.time()

        #print(f"\r{len(buffer)}", end = " ")
        
        transcription.process_buffer()


        time.sleep(0.05)
except KeyboardInterrupt:
    bot.leave_all()
finally:
    print("[MAIN] system terminated")


#if __name__ == "__main__":
    #main()
    