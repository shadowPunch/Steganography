import numpy as np
from scipy.io.wavfile import read, write
import os


def file_to_bits(filepath):
    """Reads any file and returns its content as a bit string."""
    try:
        with open(filepath, 'rb') as f:
            file_data = f.read()
        return ''.join(format(byte, '08b') for byte in file_data)
    except FileNotFoundError:
        print(f"Error: Payload file not found at {filepath}")
        return None

def encode_audio_2bit_lsb(carrier_path, payload_path, output_path):
    """Hides a payload file inside a carrier WAV file using 2-bit LSB."""
    
    print("--- Starting 2-bit LSB Encoding ---")
    try:
        sample_rate, carrier_data = read(carrier_path)
    except FileNotFoundError:
        print(f"Error: Carrier file not found at {carrier_path}")
        return

    flat_carrier = carrier_data.flatten()
    
    print(f"Reading payload file: {payload_path}")
    payload_bits = file_to_bits(payload_path)
    if payload_bits is None: return
    
    payload_size = len(payload_bits)
    size_bits = format(payload_size, '032b') # 32-bit size header
    bits_to_hide = size_bits + payload_bits
    

    carrier_capacity = len(flat_carrier) * 2
    
    if len(bits_to_hide) > carrier_capacity:
        raise ValueError(f"Payload is too large for this carrier! \n"
                         f"Needed: {len(bits_to_hide)} bits \n"
                         f"Have:   {carrier_capacity} bits")

    print(f"Hiding {len(bits_to_hide)} bits in {carrier_capacity} available bits.")


    num_samples_needed = (len(bits_to_hide) + 1) // 2
    
    for i in range(num_samples_needed):
        bit_chunk_start = i * 2
        bit_chunk = bits_to_hide[bit_chunk_start : bit_chunk_start + 2]
        
        if len(bit_chunk) == 1:
            bit_chunk += '0'
            
        bits_as_int = int(bit_chunk, 2)
        
        flat_carrier[i] = (flat_carrier[i] & ~3) | bits_as_int

    stego_data = flat_carrier.reshape(carrier_data.shape)
    
    print(f"Saving stego audio to {output_path}...")
    write(output_path, sample_rate, stego_data.astype(carrier_data.dtype))
    print("Encoding complete.")

def decode_audio_2bit_lsb(stego_path, output_payload_path):
    """Extracts a hidden file from a stego WAV file using 2-bit LSB."""
    
    print("\n--- Starting 2-bit LSB Decoding ---")
    try:
        sample_rate, stego_data = read(stego_path)
    except FileNotFoundError:
        print(f"Error: Stego file not found at {stego_path}")
        return
        
    flat_stego = stego_data.flatten()
    
    print("Extracting LSBs...")
    extracted_bits = []
    for sample in flat_stego:s
        extracted_int = sample & 3
        extracted_bits.append(format(extracted_int, '02b'))

    bits_str = "".join(extracted_bits)

    if len(bits_str) < 32:
        raise ValueError("File is too small to contain a size header.")
        
    size_bits_str = bits_str[:32]
    payload_size = int(size_bits_str, 2)
    print(f"Header found. Expecting payload of {payload_size} bits.")

    total_bits_expected = 32 + payload_size
    if len(bits_str) < total_bits_expected:
        raise ValueError(f"File is corrupted. Expected {total_bits_expected} bits, found {len(bits_str)}.")
    
    payload_bits_str = bits_str[32 : total_bits_expected]

    print("Reconstructing payload file...")
    byte_strings = [payload_bits_str[i:i+8] for i in range(0, len(payload_bits_str), 8)]
    
    byte_data = bytes([int(b_str, 2) for b_str in byte_strings if len(b_str) == 8])

    with open(output_payload_path, 'wb') as f:
        f.write(byte_data)
        
    print(f"Decoding complete. Payload saved as {output_payload_path}")
    
    
carrier_audio = "sample_audio.wav" 
payload_to_hide = "secret_image.jpg"
stego_output = "stego_2bit_output.wav"
decoded_output = "decoded_image_from_2bit.png" 

try:

    carrier_size_bytes = os.path.getsize(carrier_audio)
    payload_size_bytes = os.path.getsize(payload_to_hide)
    
    print(f"Carrier size: {carrier_size_bytes / 1024:.2f} KB")
    print(f"Payload size: {payload_size_bytes / 1024:.2f} KB")


    encode_audio_2bit_lsb(carrier_audio, payload_to_hide, stego_output)
    decode_audio_2bit_lsb(stego_output, decoded_output)

    print("\n--- Process complete ---")
    print(f"Check your folder for '{stego_output}' and '{decoded_output}'.")
    print(f"'{decoded_output}' should be a 100x100 red square.")

except (FileNotFoundError, ValueError) as e:
    print(f"\n--- An error occurred ---")
    print(e)
