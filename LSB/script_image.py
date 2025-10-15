from PIL import Image
import numpy as np

input_image_path="Sample1.jpeg"
output_image_path="image_output1.png"


def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def encode_lsb(input_image_path, message, output_image_path):
    img = Image.open(input_image_path).convert('RGB')
    data = np.array(img)

    # bits + end marker
    message += "#####END#####"
    bits = ''.join([format(ord(c), '08b') for c in message])

    flat_data = data.flatten()

    if len(bits) > len(flat_data):
        raise ValueError("Message too large to hide in this image!")

    # Embed bits into LSB
    for i in range(len(bits)):
        flat_data[i] = (flat_data[i] & 254) | int(bits[i])

    encoded_data = flat_data.reshape(data.shape)
    encoded_img = Image.fromarray(encoded_data.astype('uint8'), 'RGB')
    encoded_img.save(output_image_path)
    print("Message encoded and saved to", output_image_path)

def decode_lsb(encoded_image_path):
    img = Image.open(encoded_image_path).convert('RGB')
    data = np.array(img)
    flat_data = data.flatten()

    # Extract LSB
    bits = [str(flat_data[i] & 1) for i in range(len(flat_data))]
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    message = ''.join(chars)

    # Stop at end marker
    end_marker = "#####END#####"
    if end_marker in message:
        message = message[:message.index(end_marker)]
    else:
        message = "End marker not found or message corrupted."

    return message


encode_lsb(input_image_path, "Hello Nithish, this is hidden!", output_image_path)
print(decode_lsb(output_image_path))

