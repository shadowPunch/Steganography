
import wave
import struct
import math
import os

payload_audio_file = 'my_secret_audio.wav'
sample_rate = 44100.0 # samples per second
duration = 1.0 # second
frequency = 440.0 # Hz

try:
    with wave.open(payload_audio_file, 'wb') as wf:
        wf.setnchannels(1) # mono
        wf.setsampwidth(2) # 16-bit (2 bytes) per sample
        wf.setframerate(sample_rate)
        
        n_samples = int(duration * sample_rate)
        for i in range(n_samples):
            # Calculate the sample value
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency * (i / sample_rate)))
            # Pack the value as 2-byte signed integer
            data = struct.pack('<h', value)
            wf.writeframesraw(data)
            
    print(f"Created '{payload_audio_file}' as the payload.")
except Exception as e:
    print(f"Could not create dummy audio file: {e}")

