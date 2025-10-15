from PIL import Image
import numpy as np
import os


def file_to_bits(filepath):
    """Reads a file and returns its content as a bit string."""
    with open(filepath, 'rb') as f:

        file_data = f.read()
    

    return ''.join(format(byte, '08b') for byte in file_data)


def encode_image_lsb(carrier_image_path, payload_image_path, output_image_path):
    """Hides a payload file inside a carrier image."""
    

    img = Image.open(carrier_image_path).convert('RGB')
    data = np.array(img)
    flat_data = data.flatten()
    
    payload_bits = file_to_bits(payload_image_path)
    payload_size = len(payload_bits)
    
    size_bits = format(payload_size, '032b')
    
    
    bits_to_hide = size_bits + payload_bits
    

    total_bits_needed = len(bits_to_hide)
    carrier_capacity = len(flat_data)
    
    if total_bits_needed > carrier_capacity:
        raise ValueError(f"Payload is too large for this carrier image! \n"
                         f"Needed: {total_bits_needed} bits \n"
                         f"Have:   {carrier_capacity} bits")

    print(f"Hiding {payload_size} bits (plus 32-bit header) in {carrier_capacity} available bits.")


    for i in range(total_bits_needed):
        flat_data[i] = (flat_data[i] & 254) | int(bits_to_hide[i])


    encoded_data = flat_data.reshape(data.shape)
    encoded_img = Image.fromarray(encoded_data.astype('uint8'), 'RGB')
    encoded_img.save(output_image_path)
    print("Encoding complete. Stego image saved as", output_image_path)


def decode_image_lsb(stego_image_path, output_payload_path):
    """Extracts a hidden file from a stego image."""
    
    print(f"Decoding {stego_image_path}...")
    img = Image.open(stego_image_path).convert('RGB')
    data = np.array(img).flatten()

    # Extract all LSBs from the image
    lsb_bits = [str(d & 1) for d in data]


    if len(lsb_bits) < 32:
        raise ValueError("Image is too small to contain a 32-bit size header.")
        
    size_bits_str = "".join(lsb_bits[:32])
    payload_size = int(size_bits_str, 2)
    print(f"Header found. Expecting payload of {payload_size} bits.")


    total_bits_expected = 32 + payload_size
    if len(lsb_bits) < total_bits_expected:
        raise ValueError(f"Image is corrupted or incomplete. "
                         f"Expected {total_bits_expected} bits, found {len(lsb_bits)}.")
    
    
    payload_bits_str = "".join(lsb_bits[32 : total_bits_expected])

    byte_strings = [payload_bits_str[i:i+8] for i in range(0, len(payload_bits_str), 8)]
    
    if len(byte_strings[-1]) != 8:
        print("Warning: Final byte is incomplete. Data might be corrupt.")
        byte_strings = byte_strings[:-1] 

    byte_data = bytes([int(b_str, 2) for b_str in byte_strings])

 
    with open(output_payload_path, 'wb') as f:
        f.write(byte_data)
        
    print(f"Decoding complete. Payload saved as {output_payload_path}")


try:
    payload_img_temp = Image.new('RGB', (50, 50), color = 'red')
    payload_img_temp.save('my_secret_image.png')
    print("Created 'my_secret_image.png' as the payload.")
except Exception as e:
    print(f"Could not create dummy image: {e}")


carrier_image = "Sample1.jpeg"
payload_image = "secret_image.jpg"
stego_output = "stego_with_image.png" 
decoded_output = "decoded_secret_image.png"

try:
    
    carrier_size = os.path.getsize(carrier_image)
    payload_size = os.path.getsize(payload_image)
    print(f"Carrier size: {carrier_size} bytes, Payload size: {payload_size} bytes")


    encode_image_lsb(carrier_image, payload_image, stego_output)
    decode_image_lsb(stego_output, decoded_output)

    print("\n--- Process complete ---")
    print(f"Check your folder for '{stego_output}' and '{decoded_output}'.")
    print(f"'{decoded_output}' should be an identical red square.")

except FileNotFoundError:
    print(f"Error: Make sure '{carrier_image}' and '{payload_image}' exist.")
except ValueError as e:
    print(f"\n--- A controlled error occurred ---")
    print(e)
    print("This often happens if the payload image is too big for the carrier.") sizes for comparison
