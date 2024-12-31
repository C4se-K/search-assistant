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
    def __init__(self, send): # , ready <- assuming this is threaded
        #self.READY = ready

        self.send_queue = send

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

        self.continuing_prompt = False
        self.previous_output = ""

        self.total = ""


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

    """
    converts raw pcm data to a numpy array before appending onto the transciption buffer
    """
    def add_to_buffer(self, data): #raw_audio_queue.get()
        #print('being called')
        temp = np.frombuffer(self.preprocess_decoded(data), dtype=np.int16)
        self.buffer = np.concatenate((self.buffer, np.frombuffer(temp)))
        self.last_packet_time = time.time()
        #print(len(self.buffer))

    """
    converts opus packets recieved from  discord to raw pcm

    also resamples data to 16000 to prepare for transcription
    """
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

    """
    runs faster whisper on the data
    """
    def process_audio(self, audio, prompt_ = ""):
        start_time = time.time()
        #global buffer_count, buffer_store, total, first_sentence
        #$buffer_count += 1

        segments, _ = self.model.transcribe(audio, language="en", beam_size= 5, initial_prompt=prompt_)
        transcription = " ".join([segment.text for segment in segments])

        self.send_queue.put(f"{(time.time() - start_time):.2f} sec: {transcription}")
        print(f"{(time.time() - start_time):.2f} sec: {transcription}")


        self.total = "".join(transcription)
        self.previous_output = transcription
        #print(f"{self.total}", end = " ")

        #if transcription.endswith(".") or transcription.endswith("?") or transcription.endswith("!"):
            #first_sentence = True

    """
    buffer management 

    if data < limit and no more data, send

    if data >= limit and more data, send in bactches
    """

    """
    a potential optimization may be to reduce the number of 
    calls it get since its not doing anything in 99% of calls
    
    """
    def process_buffer(self):
        cur_time = time.time()

        if (len(self.buffer) < self.data_minimum and 
            (cur_time-self.last_packet_time) > self.silence_threshold*2):

            self.buffer = self.buffer[len(self.buffer):]
            self.continuing_prompt = False
            return

        if (len(self.buffer) < self.target_size and 
            len(self.buffer) >= self.data_minimum and 
            (cur_time-self.last_packet_time) > self.silence_threshold):

            data_size = len(self.buffer)
            audio = np.frombuffer(self.buffer[:data_size], dtype=np.int16)

            #data = buffer[:target_size]
            self.buffer = self.buffer[data_size:]
            self.process_audio(audio)
            self.continuing_prompt = False
            return


        if len(self.buffer) >= self.target_size:
            #first_sentence = False
            audio = np.frombuffer(self.buffer[:self.target_size], dtype=np.int16)

            #data = buffer[:target_size]
            self.buffer = self.buffer[self.target_size:]

            prompt = ""
            if self.continuing_prompt:
                prompt = self.previous_output

            self.process_audio(audio, prompt)
            self.continuing_prompt = True
            return

