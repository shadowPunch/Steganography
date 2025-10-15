from PIL import Image
import numpy as np

original_image_path = "Sample1.jpeg"


stego_image_path = "image_output1.png"


output_image_path = "difference_output.png"

try:

    original_img = Image.open(original_image_path).convert('RGB')
    stego_img = Image.open(stego_image_path).convert('RGB')


    if original_img.size != stego_img.size:
        raise ValueError(f"Images must be the same size! "
                         f"{original_img.size} vs {stego_img.size}")


    original_data = np.array(original_img)
    stego_data = np.array(stego_img)

    original_int = original_data.astype(np.int16)
    stego_int = stego_data.astype(np.int16)

    diff_int = original_int - stego_int
    abs_diff_int = np.absolute(diff_int)

# Cast back to uint8 (0-255) to be saved as an image
    diff_data = abs_diff_int.astype(np.uint8)


    # Multiply by 255 to make the tiny '1' values visible as '255'
    visual_data = diff_data * 255


    diff_img = Image.fromarray(visual_data, 'RGB')


    diff_img.save(output_image_path)
    print(f"Difference image saved to {output_image_path}")


    diff_img.show()

except FileNotFoundError as e:
    print(f"Error: Could not find image file. {e}")
except ValueError as e:
    print(f"Error: {e}")
