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


def encode_audio_phase(carrier_path, payload_path, output_path):
    """Hides a payload file in an audio file using Phase Coding."""
    print("--- Starting Phase Coding Encoding ---")
    try:
        sample_rate, data = read(carrier_path)
    except FileNotFoundError:
        print(f"Error: Carrier file not found at {carrier_path}")
        return


    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(float)

  
    print(f"Reading payload file: {payload_path}")
    payload_bits = file_to_bits(payload_path)
    if payload_bits is None: return
    
    payload_size = len(payload_bits)
    size_bits = format(payload_size, '032b')
    bits_to_hide = size_bits + payload_bits


    frame_size = 2048
    hop_size = frame_size // 2 # 50% overlap for smooth reconstruction
    # hide data in the phase of these frequency bins (indices)
    freq_range_to_modify = (40, 100)
    bits_per_frame = freq_range_to_modify[1] - freq_range_to_modify[0]

    num_frames = (len(data) - frame_size) // hop_size + 1
    
 
    carrier_capacity = num_frames * bits_per_frame
    if len(bits_to_hide) > carrier_capacity:
        raise ValueError(f"Payload is too large for this carrier! \n"
                         f"Needed: {len(bits_to_hide)} bits \n"
                         f"Have:   {carrier_capacity} bits")

    print(f"Hiding {len(bits_to_hide)} bits in {carrier_capacity} available bits.")
    
    stego_data = np.zeros_like(data)
    bit_index = 0
    window = np.hanning(frame_size) 


    for i in range(num_frames):
        start = i * hop_size
        end = start + frame_size
        if end > len(data): break
        
        frame = data[start:end] * window
        
  
        fft_frame = np.fft.rfft(frame)
        mags = np.abs(fft_frame)
        phases = np.angle(fft_frame)
        
        # Modify the phases
        for j in range(freq_range_to_modify[0], freq_range_to_modify[1]):
            if bit_index < len(bits_to_hide):
                bit = int(bits_to_hide[bit_index])
                if bit == 1:
                    # Shift phase by 90 degrees for a '1'
                    phases[j] += np.pi / 2
                # For a '0', we do nothing
                bit_index += 1
        
        # Reconstruct the complex numbers from original magnitudes and new phases
        new_fft_frame = mags * np.exp(1j * phases)
        
        # Apply Inverse FFT
        modified_frame = np.fft.irfft(new_fft_frame)
        
        # Overlap-add to reconstruct the signal
        stego_data[start:end] += modified_frame * window

    print(f"Saving stego audio to {output_path}...")
    # Normalize the output to prevent clipping before converting back to integer
    stego_data = (stego_data / np.max(np.abs(stego_data)) * 32767).astype(np.int16)
    write(output_path, sample_rate, stego_data)
    print("Encoding complete.")


def decode_audio_phase(stego_path, output_payload_path):
    """Extracts a hidden file from a stego audio file using Phase Coding."""
    print("\n--- Starting Phase Coding Decoding ---")
    try:
        sample_rate, stego_data = read(stego_path)
    except FileNotFoundError:
        print(f"Error: Stego file not found at {stego_path}")
        return

    if stego_data.ndim > 1:
        stego_data = stego_data[:, 0]
    stego_data = stego_data.astype(float)
    
    
    frame_size = 2048
    hop_size = frame_size // 2
    freq_range_to_modify = (40, 100)
    
    num_frames = (len(stego_data) - frame_size) // hop_size + 1
    extracted_bits = []
    window = np.hanning(frame_size)

    print("Extracting bits from phase information...")
    for i in range(num_frames):
        start = i * hop_size
        end = start + frame_size
        if end > len(stego_data): break

        frame = stego_data[start:end] * window
        fft_frame = np.fft.rfft(frame)
        phases = np.angle(fft_frame)
        
        for j in range(freq_range_to_modify[0], freq_range_to_modify[1]):
            
            if phases[j] > np.pi / 4 and phases[j] < 3 * np.pi / 4:
                extracted_bits.append('1')
            else:
                extracted_bits.append('0')
    
    bits_str = "".join(extracted_bits)


    if len(bits_str) < 32:
        raise ValueError("File is too small to contain a size header.")
        
    size_bits_str = bits_str[:32]
    payload_size = int(size_bits_str, 2)
    print(f"Header found. Expecting payload of {payload_size} bits.")
    
    total_bits_expected = 32 + payload_size
    if len(bits_str) < total_bits_expected:
        raise ValueError(f"File appears corrupted. Extracted {len(bits_str)} bits, expected {total_bits_expected}.")
        
    payload_bits_str = bits_str[32 : total_bits_expected]

    print("Reconstructing payload file...")
    byte_strings = [payload_bits_str[i:i+8] for i in range(0, len(payload_bits_str), 8)]
    byte_data = bytes([int(b, 2) for b in byte_strings if len(b) == 8])

    with open(output_payload_path, 'wb') as f:
        f.write(byte_data)
        
    print(f"Decoding complete. Payload saved as {output_payload_path}")
    
    

payload_text_file = 'my_secret_message.txt'
try:
    with open(payload_text_file, 'w') as f:
        f.write("This is a secret message hidden using phase coding. " * 5)
        f.write("It is more robust than LSB and has a higher capacity than simple DCT.")
    print(f"Created '{payload_text_file}' as the payload.")
except Exception as e:
    print(f"Could not create dummy file: {e}")


carrier_audio = "sample_audio.wav" 
payload_to_hide = payload_text_file
stego_output = "stego_phase_output.wav"
decoded_output = "decoded_message_from_phase.txt"

try:
    
    carrier_size_bytes = os.path.getsize(carrier_audio)
    payload_size_bytes = os.path.getsize(payload_to_hide)
    
    print(f"Carrier size: {carrier_size_bytes / 1024:.2f} KB")
    print(f"Payload size: {payload_size_bytes / 1024:.2f} KB")


    encode_audio_phase(carrier_path, payload_to_hide, stego_output)
    decode_audio_phase(stego_path, decoded_output)

    print("\n--- Process complete ---")
    print(f"Check your folder for '{stego_output}' and '{decoded_output}'.")
    print(f"'{decoded_output}' should contain your original secret message.")

except (FileNotFoundError, ValueError) as e:
    print(f"\n--- An error occurred ---")
    print(e)
