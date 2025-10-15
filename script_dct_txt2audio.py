import numpy as np
from scipy.io.wavfile import read, write
from scipy.fftpack import dct, idct


def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)


def encode_audio_dct(carrier_path, message, output_path):
    print(f"Reading carrier audio: {carrier_path}")
    sample_rate, data = read(carrier_path)

    if data.ndim > 1:
        data = data[:, 0]
        
    bits_to_hide = text_to_bits(message) + '1111111111111110' # "ÿþ"
    
    frame_size = 1024
    # mid-range coefficient
    coeff_index = 430
    quantization_step = 80.0

    num_frames = len(data) // frame_size
    
    if len(bits_to_hide) > num_frames:
        raise ValueError("Message too large for this carrier!")

    print(f"Hiding {len(bits_to_hide)} bits in {num_frames} available frames.")
    
    stego_data = np.copy(data).astype(float)
    bit_index = 0

    for i in range(num_frames):
        if bit_index >= len(bits_to_hide):
            break

        start, end = i * frame_size, (i + 1) * frame_size
        frame = stego_data[start:end]
        frame_dct = dct(frame, type=2, norm='ortho')
        
        # Quantization
        original_coeff = frame_dct[coeff_index]
        quantized_level = round(original_coeff / quantization_step)
        bit_to_embed = int(bits_to_hide[bit_index])
        
        # If the parity of the level (even/odd) doesn't match the bit, adjust it.
        if (quantized_level % 2) != bit_to_embed:
            # Move to the closest level with the correct parity
            if quantized_level * quantization_step > original_coeff:
                quantized_level -= 1
            else:
                quantized_level += 1
        
        frame_dct[coeff_index] = quantized_level * quantization_step

        modified_frame = idct(frame_dct, type=2, norm='ortho')
        stego_data[start:end] = modified_frame
        bit_index += 1

    print(f"Saving stego audio to {output_path}...")
    # Clip values to the valid 16-bit range before converting back to integer
    stego_data = np.clip(stego_data, -32768, 32767)
    write(output_path, sample_rate, stego_data.astype(data.dtype))
    print("Encoding complete.")


def decode_audio_dct(stego_path):
    print(f"Reading stego audio {stego_path}...")
    sample_rate, data = read(stego_path)
        
    if data.ndim > 1:
        data = data[:, 0]
        

    frame_size = 1024
    coeff_index = 430
    quantization_step = 80.0 # same
    
    num_frames = len(data) // frame_size
    extracted_bits = []

    print("Extracting bits from DCT coefficients...")
    for i in range(num_frames):
        start, end = i * frame_size, (i + 1) * frame_size
        frame = data[start:end].astype(float)
        frame_dct = dct(frame, type=2, norm='ortho')
        
        coeff_val = frame_dct[coeff_index]
        quantized_level = round(coeff_val / quantization_step)
        
        extracted_bit = str(int(quantized_level) % 2)
        extracted_bits.append(extracted_bit)


    bits_str = "".join(extracted_bits)
    chars = [bits_str[i:i+8] for i in range(0, len(bits_str), 8)]
    
    message = ""
    for c in chars:
        if len(c) < 8: break
        # exception block to handle potential non-ASCII characters from garbage bits
        try:
            ch = chr(int(c, 2))
            if message.endswith("ÿþ"): break
            message += ch
        except ValueError:
            pass 
    
    if message.endswith("ÿþ"):
        print("Decoding complete. Message found.")
        return message[:-2]
    else:
        print("Decoding failed. End marker not found.")
        return "Error: Could not find hidden message. The extracted data might still be noisy."
        

carrier_audio = "sample_audio.wav" 
message_to_hide = "Hello! I am superman" 
stego_output = "stego_dct_output.wav"

try:

    encode_audio_dct(carrier_audio, message_to_hide, stego_output)
    
    print("\n--- Decoding ---")
    decoded_message = decode_audio_dct(stego_output)
    
    print(f"\nDecoded Message: {decoded_message}")

except FileNotFoundError:
    print(f"Error: Make sure '{carrier_audio}' exists.")
except ValueError as e:
    print(f"\n--- A controlled error occurred ---")
    print(e)
