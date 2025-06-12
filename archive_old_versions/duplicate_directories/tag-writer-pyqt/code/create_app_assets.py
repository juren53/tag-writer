#!/usr/bin/env python3
# create_app_assets.py - Generate icon and splash screen for Tag Writer app

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Color constants
LIGHT_BLUE = (51, 153, 255)  # RGB for light blue
WHITE = (255, 255, 255)
DARK_BLUE = (0, 51, 153)

# Create app icon (192x192 pixels)
def create_icon():
    # Create a new image with light blue background
    icon_size = 192
    icon = Image.new('RGB', (icon_size, icon_size), LIGHT_BLUE)
    draw = ImageDraw.Draw(icon)
    
    # Try to load a font, fall back to default if not available
    try:
        # Use a bold font if available
        font = ImageFont.truetype("Arial.ttf", size=96)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Add text "TW" in the center
    # Add text "TW" in the center
    text = "TW"
    # Modern method to get text dimensions
    try:
        # First try getbbox (newer Pillow versions)
        left, top, right, bottom = font.getbbox(text)
        text_width = right - left
        text_height = bottom - top
    except AttributeError:
        # Fall back to getsize (older but not as old as textsize)
        text_width, text_height = font.getsize(text)
    position = ((icon_size - text_width) // 2, (icon_size - text_height) // 2 - 10)  # -10 for slight upward adjustment
    # Draw text with a slight shadow for depth
    draw.text((position[0]+2, position[1]+2), text, font=font, fill=(30, 100, 200))  # Shadow
    draw.text(position, text, font=font, fill=WHITE)  # Main text
    
    # Add a subtle rounded corner effect
    mask = Image.new('L', (icon_size, icon_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rectangle((0, 0, icon_size, icon_size), fill=255)
    
    # Apply a slight blur for polish
    icon = icon.filter(ImageFilter.SMOOTH)
    
    # Save the icon
    icon.save('data/icon.png')
    print("Icon created at data/icon.png")

# Create splash screen (480x800 pixels)
def create_splash_screen():
    # Create a new image with gradient background
    width, height = 480, 800
    splash = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(splash)
    
    # Create a gradient background (top to bottom)
    for y in range(height):
        # Calculate gradient color (light blue to slightly darker)
        r = int(51 + (y / height) * 20)  # Slight red increase
        g = int(153 - (y / height) * 30)  # Green decrease
        b = int(255 - (y / height) * 40)  # Blue decrease
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Try to load fonts
    try:
        # Title font
        title_font = ImageFont.truetype("Arial.ttf", size=60)
        # Loading text font
        loading_font = ImageFont.truetype("Arial.ttf", size=24)
    except IOError:
        # Fall back to default font
        title_font = ImageFont.load_default()
        loading_font = ImageFont.load_default()
    
    # Add "Tag Writer" text
    title_text = "Tag Writer"
    # Modern method to get text dimensions
    try:
        # First try getbbox (newer Pillow versions)
        left, top, right, bottom = title_font.getbbox(title_text)
        title_width = right - left
        title_height = bottom - top
    except AttributeError:
        # Fall back to getsize (older but not as old as textsize)
        title_width, title_height = title_font.getsize(title_text)
    title_position = ((width - title_width) // 2, (height // 2) - title_height)
    
    # Draw title with shadow for depth
    draw.text((title_position[0]+2, title_position[1]+2), title_text, font=title_font, fill=DARK_BLUE)  # Shadow
    draw.text(title_position, title_text, font=title_font, fill=WHITE)  # Main text
    
    # Add "Loading..." text
    loading_text = "Loading..."
    # Modern method to get text dimensions
    try:
        # First try getbbox (newer Pillow versions)
        left, top, right, bottom = loading_font.getbbox(loading_text)
        loading_width = right - left
        loading_height = bottom - top
    except AttributeError:
        # Fall back to getsize (older but not as old as textsize)
        loading_width, loading_height = loading_font.getsize(loading_text)
    loading_position = ((width - loading_width) // 2, (height // 2) + 20)
    draw.text(loading_position, loading_text, font=loading_font, fill=WHITE)
    
    # Save the splash screen
    splash.save('data/splash.png')
    print("Splash screen created at data/splash.png")

if __name__ == "__main__":
    create_icon()
    create_splash_screen()
    print("App assets created successfully.")

