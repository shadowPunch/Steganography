from PIL import Image
import os
import io

def compress_image(input_path, output_path, target_kb, max_dimension=1920):
    """
    Compresses a JPEG or PNG image to a target size in kilobytes.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the compressed image.
        target_kb (int): The desired file size in KB.
        max_dimension (int): The maximum width or height for initial resizing.
    """
    try:
        with Image.open(input_path) as img:
            original_size_kb = os.path.getsize(input_path) / 1024
            print(f"Original image size: {original_size_kb:.2f} KB")
            
            # --- 1. Handle PNG Transparency ---
            # JPEGs do not support transparency, so convert RGBA to RGB
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # --- 2. Initial Resize ---
            # Resize the image if its dimensions are larger than max_dimension
            if max(img.size) > max_dimension:
                print(f"Resizing image from {img.size} to fit within {max_dimension}px...")
                img.thumbnail((max_dimension, max_dimension))

            # --- 3. Iterative Compression ---
            # Use an in-memory buffer to avoid writing to disk repeatedly
            buffer = io.BytesIO()
            
            # Iterate from a high quality to a low quality
            for quality in range(95, 10, -5):
                buffer.seek(0) # Rewind buffer to the beginning
                buffer.truncate() # Clear the buffer
                
                # Save the image to the buffer with the current quality
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                
                # Check the size of the buffer
                current_size_kb = buffer.tell() / 1024
                
                print(f"Trying quality={quality}... Size: {current_size_kb:.2f} KB")
                
                # If we are under the target, we found our quality setting
                if current_size_kb <= target_kb:
                    break
            
            # --- 4. Save the Final Image ---
            print("\n--- Compression successful! ---")
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())
                
            final_size_kb = os.path.getsize(output_path) / 1024
            print(f"Final image saved to '{output_path}'")
            print(f"Final size: {final_size_kb:.2f} KB (Target: {target_kb} KB)")
            
            if final_size_kb > target_kb:
                print("\nWarning: Could not compress below target size even at lowest quality.")
                print("The final image is the best possible compression from this script.")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Example Usage ---

# --- CREATE A DUMMY LARGE IMAGE FIRST ---
# This creates a 2MB dummy PNG file to test the script with.
try:
    print("Creating a large dummy image for testing...")
    dummy_img = Image.new('RGB', (2000, 2000), color = 'blue')
    dummy_img_path = 'large_dummy_image.png'
    dummy_img.save(dummy_img_path, format='PNG')
    print(f"Dummy image created at '{dummy_img_path}'")
except Exception as e:
    print(f"Could not create dummy image: {e}")
# ----------------------------------------

# Define your file paths and target size
input_image_path = dummy_img_path # Or your actual 2MB image path
output_image_path = 'compressed_image.jpg'
target_size_kb = 600


compress_image(input_image_path, output_image_path, target_size_kb)
