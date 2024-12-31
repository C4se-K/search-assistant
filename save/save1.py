"""
def is_valid_speech(data, sample_rate = 16000, frame = 10):
    if len(data) != int (sample_rate * frame / 1000) *2:
        raise ValueError("[ERROR] invalid frame length for VAD")
    
    return vad.is_speech(data, sample_rate)

def handle_stream(length= 2, frame = 10):
    if not raw_audio_queue.empty():
        data = raw_audio_queue.get()
        processed_audio = preprocess_decoded(data)

        frame_size = int(target_sample_rate * frame / 1000)

        for i in range(0, len(processed_audio), frame_size):
            frarme = processed_audio[i:i + frame_size].tobytes()

            if len(frame) == frame_size * 2 and is_valid_speech(frame):
                buffer.extend(processed_audio[i:i + frame_size])
                speech_active = True
            else:
                speech_active = False

        #if len(buffer) >= current_buffer_






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
    ""
    if len(audio) != 32000:
        raise ValueError("incorrect len")
    if len(audio.shape) != 1:
        raise ValueError("incorrect shape")
    ""
    #print(f"test: sample size: {len(audio)}")

    #audio = audio.astype(np.float32) / 32768.0

    segments, _ = model.transcribe(audio, beam_size=4)

    transcription = []
    for segment in segments:
       # transcription.append(segment["text"])
       print(segment.text)

    #print(transcription)
    #return transcription



"""