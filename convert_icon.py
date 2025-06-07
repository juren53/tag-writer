from PIL import Image
import os

# Path to the input PNG file
png_path = "ICON_tw.png"

# Path to the output ICO file
ico_path = "ICON_tw.ico"

# Check if the input file exists
if not os.path.exists(png_path):
    print(f"Error: Input file '{png_path}' not found.")
    exit(1)

try:
    # Open the PNG image
    img = Image.open(png_path)
    
    # Convert and save as ICO
    img.save(ico_path, format='ICO')
    
    print(f"Conversion successful: '{png_path}' has been converted to '{ico_path}'")
    print(f"Icon file created at: {os.path.abspath(ico_path)}")
except Exception as e:
    print(f"Error during conversion: {e}")

