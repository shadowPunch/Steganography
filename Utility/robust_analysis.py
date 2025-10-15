from PIL import Image, ImageFilter
import numpy as np
from skimage.util import random_noise
import io

def calculate_ber(original_bits, recovered_bits):
    if len(original_bits) != len(recovered_bits):
        # Pad the shorter string if lengths differ due to corruption
        min_len = min(len(original_bits), len(recovered_bits))
        original_bits = original_bits[:min_len]
        recovered_bits = recovered_bits[:min_len]
        print(f"Warning: Bit strings have different lengths. Comparing first {min_len} bits.")

    if not original_bits: return 0.0

    error_count = sum(1 for i in range(len(original_bits)) if original_bits[i] != recovered_bits[i])
    
    ber_percentage = (error_count / len(original_bits)) * 100
    return ber_percentage



def attack_jpeg_compression(image, quality_level=70):

    buffer = io.BytesIO()
    image.convert('RGB').save(buffer, format='JPEG', quality=quality_level)
    buffer.seek(0)
    return Image.open(buffer)

def attack_add_noise(image):

    # Convert image to numpy array in float format (0-1 range)
    img_array = np.array(image) / 255.0
    
    # Add noise using scikit-image
    noisy_array = random_noise(img_array, mode='gaussian', var=0.01)
    
    # Convert back to PIL Image format (0-255 range)
    return Image.fromarray((noisy_array * 255).astype(np.uint8))

def attack_blur(image, radius=1):
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


stego_image = Image.open("path_to_your_stego_image.png")


attacked_image = attack_jpeg_compression(stego_image, quality_level=50)

attacked_image_path = "attacked_image.jpg"
attacked_image.save(attacked_image_path)

ber = calculate_ber(original_hidden_bits, recovered_bits_after_attack)
print(f"\nBit Error Rate after JPEG attack: {ber:.2f}%")

