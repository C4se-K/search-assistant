import threading
import discord
import time

#overrides
from discord.voice_client import VoiceClient
from discord.sinks import RecordingException, Sink
from discord.opus import DecodeManager, OpusError


"""
audio capabilities

helper classes for interface_discord_pycord
"""
#Overriding run from DecodeManager
#inspired from the following, under the MIT license
#https://github.com/Pycord-Development/pycord/blob/master/discord/opus.py#L521
class ExtendDecodeManager(DecodeManager):
    def __init__(self, client, raw_audio_queue):
        super().__init__(client)

        self.client = client
        self.decode_queue = []

        self.decoder = {}

        self._end_thread = threading.Event()

        self.RAW_AUDIO = raw_audio_queue
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target = self.run, daemon=True, name = "DecodeManager")
        self.thread.start()

    def run(self):
        #print("start override decoder")
        #print(self._end_thread.is_set())
        while not self._end_thread.is_set():
            #print(f'looping {len(self.decode_queue)}')
            try:
                data = self.decode_queue.pop(0)
            except IndexError:
                #print("error 1")
                time.sleep(0.001)
                continue
            #print(f"looping {data}")
            try:
                if data.decrypted_data is None:
                    continue
                else:
                    #print("got here")
                    data.decoded_data = self.get_decoder(data.ssrc).decode(data.decrypted_data)
            except OpusError:
                print("error occured while decoding opus")
                continue

            if data.decoded_data:
                self.RAW_AUDIO.put(f"{data.decoded_data}")
                #print(f"{data.decoded_data.hex()}")

#Overriding start_recording from VoiceClient
#inspired from the following, under the MIT license
#https://github.com/Pycord-Development/pycord/blob/master/discord/voice_client.py#L52
class ExtendVoiceClient(VoiceClient):
    def start_recording(self, sink, callback, *args, raw_audio_queue):
        #print("override complete")
        if not self.is_connected():
            raise RecordingException("Not connected to voice channel.")
        if not isinstance(sink, Sink):
            raise RecordingException("Must provide a Sink object.")
        #if not discord.opus.is_loaded():
        #discord.opus.load_opus('libopus.so')

        self.empty_socket()

        #initiate the thread for decoding the raw data from the websocket
        self.decoder = ExtendDecodeManager(self, raw_audio_queue)
        self.decoder.start()

        self.recording = True
        self.decode_queue = []

        self.sink = sink
        sink.init(self)

        #initiate the getter thread for the websocket
        t = threading.Thread(
            target=self.recv_audio,
            args=(
                sink,
                callback,
                *args,
            ),
        )
        t.start()
