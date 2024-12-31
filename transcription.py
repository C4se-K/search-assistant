from faster_whisper import WhisperModel
from scipy.signal import resample
from dotenv import load_dotenv
import numpy as np
import time
import os 

from collections import deque
import numpy as np

import webrtcvad



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


        cur_time = time.time()

        if len(buffer) < self.target_size and len(buffer) >= self.data_minimum and (cur_time-last_packet_time) > self.silence_threshold:
            data_size = len(buffer)
            audio = np.frombuffer(buffer[:data_size], dtype=np.int16)

            #data = buffer[:target_size]
            buffer = buffer[data_size:]
            self.process_audio(audio)


        if len(buffer) >= self.target_size:
            #first_sentence = False
            audio = np.frombuffer(buffer[:self.target_size], dtype=np.int16)

            #data = buffer[:target_size]
            buffer = buffer[self.target_size:]
            self.process_audio(audio)