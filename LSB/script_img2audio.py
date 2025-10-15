import numpy as np
from scipy.io.wavfile import read, write
import os
import wave
import struct
import math

def file_to_bits(filepath):
    """Reads a file and returns its content as a bit string."""
    with open(filepath, 'rb') as f:
        file_data = f.read()
    return ''.join(format(byte, '08b') for byte in file_data)

def encode_audio_lsb(carrier_path, payload_path, output_path):
    """Hides a payload file inside a carrier WAV file."""
    
    print("Reading carrier audio...")
    try:
        sample_rate, carrier_data = read(carrier_path)
    except FileNotFoundError:
        print(f"Error: Carrier file not found at {carrier_path}")
        return

    flat_carrier = carrier_data.flatten()
    
    print("Reading payload file...")
    payload_bits = file_to_bits(payload_path)
    payload_size = len(payload_bits)
    size_bits = format(payload_size, '032b')
    bits_to_hide = size_bits + payload_bits
    
    total_bits_needed = len(bits_to_hide)
    carrier_capacity = len(flat_carrier)
    
    if total_bits_needed > carrier_capacity:
        raise ValueError(f"Payload is too large for this carrier! \n"
                         f"Needed: {total_bits_needed} bits (samples) \n"
                         f"Have:   {carrier_capacity} bits (samples)")

    print(f"Hiding {total_bits_needed} bits in {carrier_capacity} available samples.")

    for i in range(total_bits_needed):
        flat_carrier[i] = (flat_carrier[i] & ~1) | int(bits_to_hide[i])


    stego_data = flat_carrier.reshape(carrier_data.shape)
    
    print(f"Saving stego audio to {output_path}...")
    write(output_path, sample_rate, stego_data.astype(carrier_data.dtype))
    print("Encoding complete.")

def decode_audio_lsb(stego_path, output_payload_path):
    """Extracts a hidden file from a stego WAV file."""
    
    print(f"Reading stego audio {stego_path}...")
    try:
        sample_rate, stego_data = read(stego_path)
    except FileNotFoundError:
        print(f"Error: Stego file not found at {stego_path}")
        return
        
    flat_stego = stego_data.flatten()
    
    print("Extracting LSBs...")
   
    lsb_bits = [str(sample & 1) for sample in flat_stego]

    
    if len(lsb_bits) < 32:
        raise ValueError("File is too small to contain a 32-bit size header.")
        
    size_bits_str = "".join(lsb_bits[:32])
    payload_size = int(size_bits_str, 2)
    print(f"Header found. Expecting payload of {payload_size} bits.")

   
    total_bits_expected = 32 + payload_size
    if len(lsb_bits) < total_bits_expected:
        raise ValueError(f"File is corrupted. Expected {total_bits_expected} bits, found {len(lsb_bits)}.")
    
    payload_bits_str = "".join(lsb_bits[32 : total_bits_expected])

    
    print("Reconstructing payload file...")
    byte_strings = [payload_bits_str[i:i+8] for i in range(0, len(payload_bits_str), 8)]
    
    byte_data = bytes([int(b_str, 2) for b_str in byte_strings if len(b_str) == 8])

    with open(output_payload_path, 'wb') as f:
        f.write(byte_data)
        
    print(f"Decoding complete. Payload saved as {output_payload_path}")
    
carrier_audio = "sample_audio.wav" 
payload_image = "sample_img.png" 
stego_output = "stego_audio_with_image.wav"
decoded_output = "decoded_secret_from_audio.png" 

try:
  
    carrier_size_bytes = os.path.getsize(carrier_audio)
    payload_size_bytes = os.path.getsize(payload_image)
    
    print(f"Carrier size: {carrier_size_bytes / 1024:.2f} KB")
    print(f"Payload size: {payload_size_bytes / 1024:.2f} KB")


    encode_audio_lsb(carrier_audio, payload_image, stego_output)
    decode_audio_lsb(stego_output, decoded_output)

    print("\n--- Process complete ---")
    print(f"Check your folder for '{stego_output}'.")
    print(f"Check your folder for '{decoded_output}' - it should be a 50x50 blue square.")

except FileNotFoundError:
    print(f"Error: Make sure '{carrier_audio}' and '{payload_image}' exist.")
except ValueError as e:
    print(f"\n--- A controlled error occurred ---")
    print(e)
