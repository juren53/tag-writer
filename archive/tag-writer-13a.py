#!/usr/bin/python3
#-----------------------------------------------------------
# ############   tag-writer.py  Ver 0.13 ################
# This program creates a GUI interface for entering and    
# writing IPTC metadata tags to TIF and JPG images selected   
# from a directory pick list using the tkinter libraries.
# This program is intended as a free form metadata tagger
# when metada can not be pulled from an online database. 
#  Created Sat 01 Jul 2023 07:37:56 AM CDT   [IPTC]
#  Updated Sun 02 Jul 2023 04:53:41 PM CDT added no-backup
#  Updated Sat 29 Mar 2025 07:51:49 PM CDT Updated to use execute_json() for robust metadata retrieval
#  Updated Sat 29 Mar 2025 07:51:49 PM CDT added read existing metadata from file for editing 
#  Updated Sun 30 Mar 2025 03:20:00 AM CDT added command-line argument support & status msg after write
#  Updated Tue 01 Apr 2025 08:55:00 AM CDT Ver .09 added export to JSON feature & clear data to Edit menu
#  Updated Wed 02 APr 2025 11:23:01 AM CSD Ver .10 added full image viewer from thumbnail & License window under Help
#  Updated Fri 04 Apr 2025 03:45:05 AM CST Ver .11 cleaned up UI & added click to exit preview
#  Updated Fri 04 Apr 2025 03:45:05 AM CST Ver .12 added zoom preview image & Alt+R Recent Access key
#  Updated Sat 05 Apr 2025 05:14:11 AM CDT Ver .13 added Description text box & arrow keys for next and previous photo
#-----------------------------------------------------------

import tkinter as tk
from tkinter import filedialog
from tkinter import Menu
from tkinter import messagebox
from tkinter import TclError
import exiftool
import argparse
import os
import sys
import io
import logging
import json
import webbrowser

# Global list to store recently accessed files (max 5)
recent_files = []
# Global variables for full image preview zoom functionality
original_image = None
full_image_original = None
full_image_zoom_factor = 1.0
filemenu = None
# Global variables for directory navigation
directory_image_files = []
current_file_index = -1
nav_prev_button = None
nav_next_button = None
# Config file for storing persistent data
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".tag_writer_config.json")
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Try to import PIL/Pillow components with fallback options
PIL_AVAILABLE = False
IMAGETK_AVAILABLE = False
try:
    from PIL import Image
    PIL_AVAILABLE = True
    try:
        from PIL import ImageTk
        IMAGETK_AVAILABLE = True
    except ImportError:
        logging.warning("ImageTk not available - thumbnail display will be disabled")
except ImportError:
    logging.warning("PIL/Pillow not available - image handling functionality will be limited")

def update_recent_files(file_path):
    """
    Updates the list of recently accessed files.
    - Adds the file_path to the beginning of the list
    - Removes duplicates
    - Limits the list to 5 entries
    - Rebuilds the recent files menu
    """
    global recent_files, recent_files_menu
    
    # Only add valid files to recent_files list
    if file_path and os.path.isfile(file_path):
        # Remove the file if it's already in the list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add the file to the beginning of the list
        recent_files.insert(0, file_path)
        
        # Limit the list to 5 items
        recent_files = recent_files[:5]
        
        # Rebuild the recent files menu if it exists
        if 'recent_files_menu' in globals() and recent_files_menu:
            build_recent_files_menu()

def build_recent_files_menu():
    """
    Builds the recent files menu from the recent_files list.
    - Clears the current menu
    - Adds an item for each recent file
    - Adds a "No recent files" disabled item if the list is empty
    """
    global recent_files_menu
    
    # Check if recent_files_menu exists in global scope
    if 'recent_files_menu' not in globals() or recent_files_menu is None:
        return
        
    # Clear all items from the menu
    recent_files_menu.delete(0, 'end')
    
    # If there are recent files, add them to the menu
    if recent_files:
        for file_path in recent_files:
            # Get the base filename for the menu label
            basename = os.path.basename(file_path)
            # Use a lambda with default argument to avoid late binding issues
            recent_files_menu.add_command(
                label=basename,
                command=lambda path=file_path: open_recent_file(path)
            )
    else:
        # If no recent files, add a disabled item
        recent_files_menu.add_command(label="No recent files", state="disabled")

def open_recent_file(file_path):
    """Opens a file from the recent files list"""
    global status_label
    
    if os.path.exists(file_path):
        select_file(file_path)
        # Update status to show navigation hint
        if 'status_label' in globals() and status_label:
            if directory_image_files and len(directory_image_files) > 1:
                status_label.config(text=f"Use ← → buttons to navigate through {len(directory_image_files)} images in folder", fg="blue")
    else:
        # If the file no longer exists, show an error and update the menu
        if 'status_label' in globals() and status_label:
            status_label.config(text=f"Error: File '{os.path.basename(file_path)}' no longer exists", fg="red")
        if file_path in recent_files:
            recent_files.remove(file_path)
            build_recent_files_menu()

def show_recent_files_menu():
    """Direct function to show the recent files submenu"""
    if 'filemenu' in globals() and filemenu and 'recent_files_menu' in globals() and recent_files_menu:
        # Find the index of the Recently accessed cascade item
        try:
            for i in range(filemenu.index("end") + 1):
                if filemenu.entrycget(i, "label") == "Recently accessed":
                    # Calculate position for popup menu
                    x = root.winfo_rootx() + 50  # offset from left of window
                    y = root.winfo_rooty() + 50  # offset from top of window
                    recent_files_menu.post(x, y)
                    return
        except Exception as e:
            logging.error(f"Error showing recent files menu: {str(e)}")

def open_recent_menu(event=None):
    """Open the Recently accessed files menu when Alt+R is pressed"""
    logging.info("Alt+R shortcut pressed - attempting to open recent files menu")
    try:
        # Get the menubar
        menubar = root.nametowidget(root.cget("menu"))
        
        # Find the File menu
        file_menu_index = None
        for i in range(menubar.index("end") + 1):
            try:
                if menubar.entrycget(i, "label") == "File":
                    file_menu_index = i
                    break
            except TclError:
                continue
        
        if file_menu_index is not None:
            logging.info(f"Found File menu at index {file_menu_index}")
            
            # Get the File menu widget
            file_menu = menubar.nametowidget(menubar.entryconfigure(file_menu_index, "menu")[4])
            
            # Find the Recently accessed submenu
            recent_index = None
            for i in range(file_menu.index("end") + 1):
                try:
                    if file_menu.entrycget(i, "label") == "Recently accessed":
                        recent_index = i
                        break
                except TclError:
                    continue
            
            if recent_index is not None:
                logging.info(f"Found Recently accessed menu at index {recent_index}")
                
                # Calculate position relative to the window
                x = root.winfo_rootx() + 100
                y = root.winfo_rooty() + 100
                
                # Get the submenu widget
                submenu = file_menu.nametowidget(file_menu.entryconfigure(recent_index, "menu")[4])
                
                # Post the submenu directly
                logging.info(f"Posting recent files menu at coordinates {x}, {y}")
                submenu.post(x, y)
                return True
            else:
                logging.error("Could not find 'Recently accessed' menu item")
        else:
            logging.error("Could not find 'File' menu")
    except Exception as e:
        logging.error(f"Error opening recent files menu: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
    
    return False
def save_recent_files():
    """
    Save the recent_files list to the config file.
    """
    try:
        config_data = {"recent_files": recent_files}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f)
        logging.debug(f"Recent files saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        logging.error(f"Error saving recent files: {str(e)}")
        return False

def load_recent_files():
    """
    Load the recent_files list from the config file.
    Returns True if successful, False otherwise.
    """
    global recent_files
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
                if "recent_files" in config_data:
                    # Filter out files that no longer exist
                    recent_files = [f for f in config_data["recent_files"] if os.path.isfile(f)]
                    logging.debug(f"Loaded {len(recent_files)} recent files from {CONFIG_FILE}")
                    return True
    except Exception as e:
        logging.error(f"Error loading recent files: {str(e)}")
    return False

def get_directory_image_files(directory=None):
    """Get a sorted list of all image files in the given directory."""
    global directory_image_files
    
    if directory is None and selected_file:
        # Use directory of the currently selected file
        directory = os.path.dirname(selected_file)
    elif directory is None:
        # Use current working directory if no directory specified
        directory = os.getcwd()
    
    # Define supported image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff', '.bmp']
    
    # Get all files in the directory
    try:
        all_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                     if os.path.isfile(os.path.join(directory, f))]
        
        # Filter for image files only
        image_files = [f for f in all_files 
                      if os.path.splitext(f)[1].lower() in image_extensions]
        
        # Sort alphabetically
        directory_image_files = sorted(image_files, key=lambda x: os.path.basename(x).lower())
        
        logging.debug(f"Found {len(directory_image_files)} image files in {directory}")
        return directory_image_files
    except Exception as e:
        logging.error(f"Error getting directory image files: {str(e)}")
        directory_image_files = []
        return []

def navigate_to_file(direction):
    """Navigate to the previous or next file in the directory."""
    global selected_file, current_file_index, directory_image_files, status_label
    
    if not directory_image_files:
        logging.debug("No image files in directory to navigate")
        return
    
    # Calculate the new index
    new_index = current_file_index + direction
    
    # Check if the new index is valid
    if 0 <= new_index < len(directory_image_files):
        # Update the selected file and load it
        selected_file = directory_image_files[new_index]
        current_file_index = new_index
        
        # Update the filename label
        if 'filename_label' in globals() and filename_label:
            filename_label.config(text=f"File: {os.path.basename(selected_file)}")
        
        # Read metadata, update thumbnail, and update recent files list
        read_metadata()
        update_thumbnail()
        update_recent_files(selected_file)
        
        # Update navigation button states
        update_navigation_buttons()
        
        # Update status label with navigation information
        if 'status_label' in globals() and status_label:
            status_label.config(
                text=f"Navigated to file {current_file_index+1} of {len(directory_image_files)}: {os.path.basename(selected_file)}", 
                fg="blue"
            )
        
        logging.debug(f"Navigated to file {current_file_index+1} of {len(directory_image_files)}: {os.path.basename(selected_file)}")
    else:
        logging.debug(f"Cannot navigate: index {new_index} out of range (0-{len(directory_image_files)-1})")

def update_navigation_buttons():
    """Update the enabled/disabled state of navigation buttons based on current file index."""
    global current_file_index, nav_prev_button, nav_next_button, directory_image_files
    
    if nav_prev_button is None or nav_next_button is None:
        return
    
    # Disable both buttons if no image files or no file selected
    if not directory_image_files or current_file_index < 0:
        nav_prev_button.config(state=tk.DISABLED)
        nav_next_button.config(state=tk.DISABLED)
        return
    
    # Update previous button state
    if current_file_index <= 0:
        nav_prev_button.config(state=tk.DISABLED)
    else:
        nav_prev_button.config(state=tk.NORMAL)
    
    # Update next button state
    if current_file_index >= len(directory_image_files) - 1:
        nav_next_button.config(state=tk.DISABLED)
    else:
        nav_next_button.config(state=tk.NORMAL)

def navigate_to_file(direction):
    """Navigate to the previous or next file in the directory."""
    global selected_file, current_file_index, directory_image_files, status_label
    
    if not directory_image_files:
        logging.debug("No image files in directory to navigate")
        return
    
    # Calculate the new index
    new_index = current_file_index + direction
    
    # Check if the new index is valid
    if 0 <= new_index < len(directory_image_files):
        # Update the selected file and load it
        selected_file = directory_image_files[new_index]
        current_file_index = new_index
        
        # Update the filename label
        if 'filename_label' in globals() and filename_label:
            filename_label.config(text=f"File: {os.path.basename(selected_file)}")
        
        # Read metadata, update thumbnail, and update recent files list
        read_metadata()
        update_thumbnail()
        update_recent_files(selected_file)
        
        # Update navigation button states
        update_navigation_buttons()
        
        # Update status label with navigation information
        if 'status_label' in globals() and status_label:
            status_label.config(
                text=f"Navigated to file {current_file_index+1} of {len(directory_image_files)}: {os.path.basename(selected_file)}", 
                fg="blue"
            )
        
        logging.debug(f"Navigated to file {current_file_index+1} of {len(directory_image_files)}: {os.path.basename(selected_file)}")
    else:
        logging.debug(f"Cannot navigate: index {new_index} out of range (0-{len(directory_image_files)-1})")

def prev_file():
    """Load the previous file in the directory."""
    navigate_to_file(-1)

def next_file():
    """Load the next file in the directory."""
    navigate_to_file(1)

def select_file(file_path=None):
    global selected_file, filename_label, current_file_index, directory_image_files
    if file_path:
        if os.path.isfile(file_path):
            selected_file = file_path
            # Update the filename label if it exists
            if 'filename_label' in globals() and filename_label:
                filename_label.config(text=f"File: {os.path.basename(selected_file)}")
            read_metadata()  # Read metadata after selecting the file
            update_thumbnail()  # Update the thumbnail display
            update_recent_files(file_path)  # Update the recent files list
            
            # Update directory_image_files if needed
            directory = os.path.dirname(selected_file)
            if not directory_image_files or os.path.dirname(directory_image_files[0]) != directory:
                get_directory_image_files(directory)
            
            # Find the index of the selected file in the directory_image_files list
            try:
                current_file_index = directory_image_files.index(selected_file)
            except ValueError:
                current_file_index = -1
                
            # Update navigation button states
            update_navigation_buttons()
        else:
            print(f"Error: The file '{file_path}' does not exist or is not accessible.")
            sys.exit(1)
    else:
        selected_file = filedialog.askopenfilename(title="Select")
        if selected_file:  # Only update if a file was actually selected
            # Update the filename label if it exists
            if 'filename_label' in globals() and filename_label:
                filename_label.config(text=f"File: {os.path.basename(selected_file)}")
            read_metadata()  # Read metadata after selecting the file
            update_thumbnail()  # Update the thumbnail display
            update_recent_files(selected_file)  # Update the recent files list
            
            # Update directory_image_files
            directory = os.path.dirname(selected_file)
            get_directory_image_files(directory)
            
            # Find the index of the selected file in the directory_image_files list
            try:
                current_file_index = directory_image_files.index(selected_file)
            except ValueError:
                current_file_index = -1
                
            # Update navigation button states
            update_navigation_buttons()

def get_metadata(file_path):
    """Retrieve metadata from the specified file using execute_json() method."""
    with exiftool.ExifTool() as et:
        # Use execute_json to get metadata in JSON format
        metadata_json = et.execute_json("-j", file_path)
        
        # metadata_json returns a list of dictionaries, with one dict per file
        # Since we're only processing one file, we take the first element
        if metadata_json and len(metadata_json) > 0:
            return metadata_json[0]
        else:
            return {}

def read_metadata():
    if not selected_file:
        print("No file selected!")
        return

    metadata = get_metadata(selected_file)  # Use the new get_metadata function
    
    # Define a helper function to safely get metadata values
    def safe_get(metadata, key, default=''):
        """Safely retrieve a value from metadata with a default if not found."""
        # Try several possible prefixes for IPTC metadata
        possible_keys = [
            f'IPTC:{key}',  # Standard IPTC prefix
            key,            # Direct key
            f'XMP:{key}',   # XMP prefix
            f'EXIF:{key}'   # EXIF prefix
        ]
        
        for possible_key in possible_keys:
            if possible_key in metadata:
                value = metadata[possible_key]
                # Convert to string if not already
                if value is None:
                    return default
                return str(value)
        
        return default

    # Populate the entry fields with existing metadata
    entry_headline.delete(0, tk.END)
    entry_headline.insert(0, safe_get(metadata, 'Headline'))
    
    entry_credit.delete(0, tk.END)
    entry_credit.insert(0, safe_get(metadata, 'Credit'))
    
    entry_object_name.delete(0, tk.END)
    entry_object_name.insert(0, safe_get(metadata, 'ObjectName'))
    
    text_caption_abstract.delete("1.0", tk.END)
    text_caption_abstract.insert("1.0", safe_get(metadata, 'Caption-Abstract'))
    
    entry_writer_editor.delete(0, tk.END)
    entry_writer_editor.insert(0, safe_get(metadata, 'Writer-Editor'))
    
    entry_by_line.delete(0, tk.END)
    entry_by_line.insert(0, safe_get(metadata, 'By-line'))
    
    entry_source.delete(0, tk.END)
    entry_source.insert(0, safe_get(metadata, 'Source'))
    
    entry_date.delete(0, tk.END)
    entry_date.insert(0, safe_get(metadata, 'DateCreated'))
    
    entry_copyright_notice.delete(0, tk.END)
    entry_copyright_notice.insert(0, safe_get(metadata, 'CopyrightNotice'))

def write_metadata():
    global status_label
    if not selected_file:
        print("No file selected!")
        status_label.config(text="Error: No file selected!", fg="red")
        return

    Headline = entry_headline.get()
    Credit = entry_credit.get()
    ObjectName = entry_object_name.get()
    CaptionAbstract = text_caption_abstract.get("1.0", "end-1c")
    WriterEditor = entry_writer_editor.get()
    By_line = entry_by_line.get()
    Source = entry_source.get()
    Date = entry_date.get()
    CopyrightNotice = entry_copyright_notice.get()

    with exiftool.ExifTool() as et:
        # Set the save_backup parameter to False
        et.save_backup = False

        et.execute(b"-Headline=" + Headline.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Credit=" + Credit.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-ObjectName=" + ObjectName.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Caption-Abstract=" + CaptionAbstract.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Writer-Editor=" + WriterEditor.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-By-line=" + By_line.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-Source=" + Source.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-DateCreated=" + Date.encode('utf-8'), selected_file.encode('utf-8'))
        et.execute(b"-CopyrightNotice=" + CopyrightNotice.encode('utf-8'), selected_file.encode('utf-8'))

    print("Metadata written successfully!")
    status_label.config(text="Metadata written successfully!", fg="green")

def export_metadata_to_json():
    """Export metadata from selected file to a JSON file."""
    global status_label
    if not selected_file:
        print("No file selected!")
        status_label.config(text="Error: No file selected!", fg="red")
        return

    try:
        # Get metadata from the selected file
        metadata = get_metadata(selected_file)
        
        # Extract base filename from selected_file and change extension to .json
        base_filename = os.path.basename(selected_file)
        base_name_without_ext = os.path.splitext(base_filename)[0]
        default_json_filename = f"{base_name_without_ext}.json"
        
        # Prompt user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save metadata as JSON",
            initialfile=default_json_filename
        )
        
        # If user cancels the dialog
        if not file_path:
            return
            
        # Write metadata to JSON file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(metadata, json_file, indent=4)
            
        print(f"Metadata exported successfully to {file_path}")
        status_label.config(text=f"Metadata exported successfully!", fg="green")
        
    except Exception as e:
        error_msg = f"Error exporting metadata: {str(e)}"
        print(error_msg)
        status_label.config(text=error_msg, fg="red")

def clear_metadata_fields():
    """Clear all metadata entry fields and update status label."""
    global status_label
    
    # Clear all entry fields
    entry_headline.delete(0, tk.END)
    text_caption_abstract.delete("1.0", tk.END)
    entry_credit.delete(0, tk.END)
    entry_object_name.delete(0, tk.END)
    entry_writer_editor.delete(0, tk.END)
    entry_by_line.delete(0, tk.END)
    entry_source.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    entry_copyright_notice.delete(0, tk.END)
    
    # Update status label
    status_label.config(text="All fields cleared", fg="green")
def update_thumbnail():
    """Load the selected image file and display it as a thumbnail with robust error handling."""
    global selected_file, thumbnail_label, thumbnail_image, original_image
    
    logging.debug("=== THUMBNAIL DEBUGGING START ===")
    logging.debug(f"Update thumbnail called for file: {selected_file}")
    
    # Clear previous thumbnail
    if 'thumbnail_label' in globals() and thumbnail_label:
        logging.debug("Clearing previous thumbnail")
        thumbnail_label.config(image='')
    else:
        logging.debug("No thumbnail_label found in globals")
    
    # If no file is selected, show appropriate message and return early
    if not selected_file:
        logging.debug("No file selected, aborting thumbnail update")
        if 'thumbnail_label' in globals() and thumbnail_label:
            thumbnail_label.config(text="No image to display", image='')
        return
    
    # If PIL is not available, show appropriate message and return early
    if not PIL_AVAILABLE:
        logging.debug("PIL/Pillow not available, cannot proceed with thumbnail creation")
        if 'thumbnail_label' in globals() and thumbnail_label:
            thumbnail_label.config(text="Image preview not available\n(PIL/Pillow library not installed)", image='')
        return
    
    try:
        # Try to determine if the file is an image without opening it
        file_ext = os.path.splitext(selected_file)[1].lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff', '.bmp']
        
        logging.debug(f"Checking file extension: {file_ext}")
        if file_ext not in image_extensions:
            logging.debug(f"File extension {file_ext} not recognized as an image type")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Not an image file\nFile type: {file_ext}", image='')
            return
        
        # Try to open the image
        try:
            logging.debug(f"Attempting to open image file: {selected_file}")
            img = Image.open(selected_file)
            # Store the original image for zoom functionality
            # Store the original image
            original_image = img.copy()
            original_width, original_height = img.size
            img_format = img.format
            img_mode = img.mode
            
            logging.debug(f"Image successfully opened: {img_format} format, {img_mode} mode")
            logging.debug(f"Original dimensions: {original_width}x{original_height} pixels")
            
            # Also print to console for immediate feedback
            print(f"DEBUG: Loaded image: {os.path.basename(selected_file)}")
            print(f"DEBUG: Format: {img_format}, Mode: {img_mode}, Size: {original_width}x{original_height}")
        except Exception as e:
            logging.error(f"Error opening image: {str(e)}")
            print(f"ERROR: Failed to open image: {str(e)}")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Cannot open image:\n{str(e)[:30]}...", image='')
            return
        
        # Calculate new dimensions while maintaining aspect ratio
        max_size = (200, 200)
        logging.debug(f"Resizing image to maximum dimensions: {max_size}")
        
        # No need to store original image again - we already have it in original_image
        
        try:
            # LANCZOS was introduced in Pillow 9.1.0, use ANTIALIAS for older versions as fallback
            try:
                logging.debug("Attempting to resize using LANCZOS filter")
                img.thumbnail(max_size, Image.LANCZOS)
                logging.debug("Successfully resized using LANCZOS")
            except AttributeError as e:
                logging.debug(f"LANCZOS not available: {str(e)}, trying ANTIALIAS")
                try:
                    img.thumbnail(max_size, Image.ANTIALIAS)
                    logging.debug("Successfully resized using ANTIALIAS")
                except AttributeError as e2:
                    logging.debug(f"ANTIALIAS not available: {str(e2)}, using default method")
                    # If neither is available, use the default method
                    img.thumbnail(max_size)
                    logging.debug("Successfully resized using default method")
            
            # Log the new dimensions
            new_width, new_height = img.size
            logging.debug(f"Resized dimensions: {new_width}x{new_height} pixels")
            print(f"DEBUG: Resized to: {new_width}x{new_height}")
        except Exception as e:
            logging.error(f"Error resizing image: {str(e)}")
            print(f"ERROR: Failed to resize image: {str(e)}")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Cannot resize image:\n{str(e)[:30]}...", image='')
            return
        
        # Check if ImageTk is available before trying to create PhotoImage
        if not IMAGETK_AVAILABLE:
            logging.debug("ImageTk not available, cannot create PhotoImage")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text="ImageTk not available\nCannot display preview", image='')
                thumbnail_label.config(bg="light gray")  # Visual indicator
            return
            
        # Try to convert to PhotoImage for tkinter display
        try:
            logging.debug("Creating PhotoImage from resized image")
            photo_img = ImageTk.PhotoImage(img)
            logging.debug(f"PhotoImage created successfully, dimensions: {photo_img.width()}x{photo_img.height()}")
            print(f"DEBUG: PhotoImage created: {photo_img.width()}x{photo_img.height()}")
            
            # Check if the PhotoImage dimensions match the resized image
            if photo_img.width() != new_width or photo_img.height() != new_height:
                logging.warning(f"PhotoImage dimensions ({photo_img.width()}x{photo_img.height()}) don't match resized image ({new_width}x{new_height})")
            
            thumbnail_image = photo_img  # Store reference to prevent garbage collection
            logging.debug("Reference to PhotoImage stored in thumbnail_image global variable")
            
            # Update the thumbnail display
            if 'thumbnail_label' in globals() and thumbnail_label:
                logging.debug("Updating thumbnail_label with the new image")
                # Configure the label with the new image and ensure it fills the available space
                thumbnail_label.config(image=thumbnail_image, text="", width=photo_img.width(), height=photo_img.height())
                # Force the thumbnail_label to maintain the image's size
                thumbnail_label.image = thumbnail_image  # Keep a reference to prevent garbage collection
                logging.debug("Successfully updated thumbnail_label")
                
                # Verify that the label is visible and correctly positioned
                logging.debug(f"thumbnail_label dimensions: {thumbnail_label.winfo_width()}x{thumbnail_label.winfo_height()}")
                logging.debug(f"thumbnail_label visibility: {'visible' if thumbnail_label.winfo_ismapped() else 'not visible'}")
                print(f"DEBUG: Label dimensions: {thumbnail_label.winfo_width()}x{thumbnail_label.winfo_height()}")
                print(f"DEBUG: Label visibility: {'visible' if thumbnail_label.winfo_ismapped() else 'not visible'}")
            else:
                logging.error("thumbnail_label not found or not properly initialized")
        except Exception as e:
            logging.error(f"Error creating PhotoImage: {str(e)}")
            print(f"ERROR: Failed to create PhotoImage: {str(e)}")
            if 'thumbnail_label' in globals() and thumbnail_label:
                thumbnail_label.config(text=f"Cannot create thumbnail:\n{str(e)[:30]}...", image='')
    except Exception as e:
        # Catch-all for any other errors
        logging.error(f"Unexpected error in thumbnail display: {str(e)}")
        print(f"ERROR: Unexpected error in thumbnail display: {str(e)}")
        if 'thumbnail_label' in globals() and thumbnail_label:
            thumbnail_label.config(text=f"Error displaying preview:\n{str(e)[:30]}...", image='')
    
    logging.debug("=== THUMBNAIL DEBUGGING END ===")
    # Force update the GUI to ensure changes are visible
    if 'root' in globals():
        try:
            root.update_idletasks()
            # Print updated label dimensions for debugging
            if 'thumbnail_label' in globals() and thumbnail_label:
                print(f"DEBUG: After update_idletasks - Label dimensions: {thumbnail_label.winfo_width()}x{thumbnail_label.winfo_height()}")
                print(f"DEBUG: After update_idletasks - Label visibility: {'visible' if thumbnail_label.winfo_ismapped() else 'not visible'}")
            logging.debug("Forced GUI update via update_idletasks()")
        except Exception as e:
            logging.error(f"Error updating GUI: {str(e)}")
def zoom_full_image(event):
    """Handle zoom events with mouse-centered zooming."""
    global full_image_zoom_factor, full_image_original, image_canvas, zoom_info_label
    
    # Check if we have an original image to zoom
    if full_image_original is None:
        return
    
    # 1. Get current mouse position relative to canvas
    mouse_x = image_canvas.canvasx(event.x)
    mouse_y = image_canvas.canvasy(event.y)
    
    # Get current canvas dimensions
    canvas_width = image_canvas.winfo_width()
    canvas_height = image_canvas.winfo_height()
    
    # Get original image dimensions
    original_width, original_height = full_image_original.size
    
    # 2. Calculate relative position (as a fraction of the image)
    # This is the point we want to keep fixed during zoom
    rel_x = mouse_x / (original_width * full_image_zoom_factor)
    rel_y = mouse_y / (original_height * full_image_zoom_factor)
    
    # 3. Update zoom factor based on scroll direction
    old_zoom = full_image_zoom_factor
    zoom_step = 0.1
    
    # Handle different mouse wheel events based on platform
    if event.num == 4 or event.delta > 0:  # Scroll up or forward (zoom in)
        full_image_zoom_factor += zoom_step
    elif event.num == 5 or event.delta < 0:  # Scroll down or backward (zoom out)
        full_image_zoom_factor -= zoom_step
    
    # Limit zoom factor to reasonable range (10% to 500%)
    full_image_zoom_factor = max(0.1, min(5.0, full_image_zoom_factor))
    
    # Log zoom event
    logging.debug(f"Zoom event: {old_zoom:.2f} -> {full_image_zoom_factor:.2f}, mouse at ({rel_x:.2f}, {rel_y:.2f})")
    
    try:
        # 4. Resize the image with new zoom factor
        new_width = int(original_width * full_image_zoom_factor)
        new_height = int(original_height * full_image_zoom_factor)
        
        # Calculate where the mouse point should be after zooming
        new_mouse_x = rel_x * new_width
        new_mouse_y = rel_y * new_height
        
        # Resize the image using appropriate method
        try:
            zoomed_img = full_image_original.resize((new_width, new_height), Image.LANCZOS)
        except AttributeError:
            try:
                zoomed_img = full_image_original.resize((new_width, new_height), Image.ANTIALIAS)
            except AttributeError:
                zoomed_img = full_image_original.resize((new_width, new_height))
        
        # 5. Update canvas with new image
        if IMAGETK_AVAILABLE:
            photo_img = ImageTk.PhotoImage(zoomed_img)
            
            # Update the canvas image
            image_canvas.delete("all")
            image_canvas.create_image(0, 0, image=photo_img, anchor="nw")
            image_canvas.image = photo_img  # Keep a reference
            
            # Update the scroll region to match the new image size
            image_canvas.config(scrollregion=(0, 0, new_width, new_height))
            
            # 6. Scroll to keep the mouse point at the same relative position
            # Calculate the new scroll position
            viewport_left = new_mouse_x - (canvas_width / 2)
            viewport_top = new_mouse_y - (canvas_height / 2)
            
            # Ensure the scroll position is within bounds
            viewport_left = max(0, min(viewport_left, new_width - canvas_width))
            viewport_top = max(0, min(viewport_top, new_height - canvas_height))
            
            # Move the canvas view
            image_canvas.xview_moveto(viewport_left / new_width if new_width > 0 else 0)
            image_canvas.yview_moveto(viewport_top / new_height if new_height > 0 else 0)
            
            # 7. Update info labels
            zoom_percent = int(full_image_zoom_factor * 100)
            if 'zoom_info_label' in globals() and zoom_info_label:
                zoom_info_label.config(text=f"Zoom: {zoom_percent}% | Dimensions: {new_width}x{new_height} px")
    
    except Exception as e:
        logging.error(f"Error during image zoom: {str(e)}")
        print(f"ERROR: Failed to zoom image: {str(e)}")

def show_full_image():
    """
    Displays the full-sized version of the currently selected image in a new window.
    
    Features:
    - Creates a new Toplevel window with the image filename as part of the title
    - Uses a canvas with scrollbars to display the image
    - Supports mouse-centered zooming with the mouse wheel
    - Handles potential errors gracefully with appropriate user feedback
    """
    global selected_file, root, full_image_original, full_image_zoom_factor, image_canvas, zoom_info_label
    
    # Check if a file is selected
    if not selected_file:
        messagebox.showinfo("No Image", "No image file is currently selected.")
        return
    
    # Check if PIL is available
    if not PIL_AVAILABLE:
        messagebox.showerror("Feature Unavailable", 
                            "Cannot display full image. PIL/Pillow library is not installed.")
        return
    
    try:
        # Create new window
        img_window = tk.Toplevel(root)
        img_window.title(f"Full Image: {os.path.basename(selected_file)}")
        
        # Calculate maximum display size (80% of screen dimensions)
        screen_width = img_window.winfo_screenwidth()
        screen_height = img_window.winfo_screenheight()
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)
        
        # Load the image and get original dimensions
        img = Image.open(selected_file)
        original_width, original_height = img.size
        
        # Store original image for zooming and reset zoom factor
        full_image_original = img.copy()
        full_image_zoom_factor = 1.0
        
        # Calculate the scaling factor if image is too large for initial display
        scale_width = max_width / original_width if original_width > max_width else 1
        scale_height = max_height / original_height if original_height > max_height else 1
        scale = min(scale_width, scale_height)
        
        # Resize image if necessary for initial display
        display_width = original_width
        display_height = original_height
        
        if scale < 1:
            display_width = int(original_width * scale)
            display_height = int(original_height * scale)
            
            # Use appropriate resampling method based on PIL version
            try:
                img = img.resize((display_width, display_height), Image.LANCZOS)
            except AttributeError:
                try:
                    img = img.resize((display_width, display_height), Image.ANTIALIAS)
                except AttributeError:
                    img = img.resize((display_width, display_height))
        
        # Create a frame for canvas and scrollbars
        canvas_frame = tk.Frame(img_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add horizontal and vertical scrollbars
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        # Create canvas widget for displaying image with scrollbars
        canvas_width = min(display_width, max_width)
        canvas_height = min(display_height, max_height)
        
        image_canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height,
                                xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set,
                                cursor="hand2")  # Hand cursor to indicate clickability
        
        # Configure scrollbars
        h_scrollbar.config(command=image_canvas.xview)
        v_scrollbar.config(command=image_canvas.yview)
        
        # Pack scrollbars and canvas
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Convert to PhotoImage for display
        if IMAGETK_AVAILABLE:
            photo_img = ImageTk.PhotoImage(img)
            
            # Add the image to the canvas
            image_canvas.create_image(0, 0, image=photo_img, anchor="nw")
            image_canvas.image = photo_img  # Keep a reference
            
            # Configure canvas scrolling
            image_canvas.config(scrollregion=(0, 0, display_width, display_height))
            
            # Bind mouse wheel events for zoom functionality
            image_canvas.bind("<MouseWheel>", zoom_full_image)  # Windows, macOS
            image_canvas.bind("<Button-4>", zoom_full_image)    # Linux scroll up
            image_canvas.bind("<Button-5>", zoom_full_image)    # Linux scroll down
            
            # Bind mouse click to close the window
            image_canvas.bind("<Button-1>", lambda e: img_window.destroy())
            
            # Add info panel below the canvas
            info_frame = tk.Frame(img_window)
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Add dimension information
            if scale < 1:
                info_text = f"Scaled image: {display_width}x{display_height} (Original: {original_width}x{original_height})"
            else:
                info_text = f"Original size: {original_width}x{original_height}"
            
            info_label = tk.Label(info_frame, text=info_text)
            info_label.pack(pady=5)
            
            # Add zoom information label
            zoom_info_label = tk.Label(info_frame, text=f"Zoom: 100% | Dimensions: {display_width}x{display_height} px")
            zoom_info_label.pack(pady=2)
            
            # Add close button
            close_button = tk.Button(info_frame, text="Close", command=img_window.destroy)
            close_button.pack(pady=10)
            
            # Set focus to window and keyboard shortcuts
            img_window.focus_set()
            img_window.bind("<Escape>", lambda e: img_window.destroy())
            
            # Update window to ensure it's ready
            img_window.update()
            
        else:
            # ImageTk not available
            messagebox.showerror("Display Error", 
                                "Cannot display image preview. ImageTk module is not available.")
            img_window.destroy()
    
    except Exception as e:
        # Handle any errors
        logging.error(f"Error displaying full image: {str(e)}")
        messagebox.showerror("Error", f"Failed to display image: {str(e)}")
        if 'img_window' in locals() and img_window:
            img_window.destroy()

def start_gui(initial_file=None):
    global root, entry_headline, text_caption_abstract, entry_credit, entry_object_name
    global entry_writer_editor, entry_by_line, entry_source, entry_date, entry_copyright_notice, selected_file
    global status_label, filename_label, thumbnail_label, thumbnail_image, recent_files_menu
    # Create the GUI window
    root = tk.Tk()
    root.title("Metadata Tag Writer")
    
    root.geometry("1000x600")     # sets default window size
    root.configure(padx=5, pady=5)  # Add padding around the main window
    
    # Set the application icon
    try:
        if PIL_AVAILABLE and IMAGETK_AVAILABLE:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ICON_tw.png")
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_image)
                root.iconphoto(True, icon_photo)
                logging.info(f"Successfully set application icon from {icon_path}")
            else:
                logging.warning(f"Icon file not found: {icon_path}")
        else:
            logging.warning("Cannot set application icon: PIL/Pillow or ImageTk not available")
    except Exception as e:
        logging.error(f"Error setting application icon: {str(e)}")
    
    # Load recent files from config file
    load_recent_files()
    
    # Add function to exit application when 'q' is pressed
    def quit_app(event=None):
        save_recent_files()  # Save recent files before closing
        root.destroy()
    
    # Bind the 'q' key to the quit_app function
    root.bind('<q>', quit_app)
    
    # Bind Alt+R to open the Recent files menu
    root.bind_all("<Alt-r>", open_recent_menu)  # Bind to all widgets
    
    # Function to show About dialog
    def show_about_dialog():
        messagebox.showinfo(
            "About Tag Writer",
            "Tag Writer\n\n"
            "Version: 0.12\n\n"
            "A tool for viewing and editing IPTC metadata in image files.\n\n"
            "© 2025 Juren"
        )
    
    # Function to display license information
    def show_license_dialog():
        # Create a new toplevel window for the license dialog
        license_window = tk.Toplevel(root)
        license_window.title("License Information")
        license_window.geometry("600x400")
        license_window.resizable(True, True)
        
        # Set minimum size to ensure the text is readable
        license_window.minsize(500, 300)
        
        # Create a label with the license text using 10pt Ubuntu font
        license_text = """         tag-writer


tag-writer is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

tag-writer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with tag-writer. If not, see: https://www.gnu.org/licenses/

Source code available at https://github.com/juren53/tag-writer/blob/main/code/tag-writer.py"""
        
        license_label = tk.Label(license_window, 
                                text=license_text, 
                                font=("Ubuntu", 10),
                                justify=tk.LEFT,
                                wraplength=550,
                                padx=20, pady=20)
        license_label.pack(expand=True, fill=tk.BOTH)
        
        # Add a close button
        close_button = tk.Button(license_window, text="Close", command=license_window.destroy)
        close_button.pack(pady=10)
        
        # Make the window modal
        license_window.transient(root)
        license_window.grab_set()
        license_window.focus_set()
        
        # Center the window on the screen
        license_window.update_idletasks()
        width = license_window.winfo_width()
        height = license_window.winfo_height()
        x = (license_window.winfo_screenwidth() // 2) - (width // 2)
        y = (license_window.winfo_screenheight() // 2) - (height // 2)
        license_window.geometry(f"{width}x{height}+{x}+{y}")
        
    # Function to open the usage guide in web browser
    def open_usage_guide():
        webbrowser.open("https://github.com/juren53/tag-writer/blob/main/Docs/tag-writer-help.md")
        
    menubar = Menu(root)
    root.config(menu=menubar)
    
    filemenu = Menu(menubar)
    menubar.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Open", command=select_file)
    
    # Create a submenu for recently accessed files
    global recent_files_menu
    recent_files_menu = Menu(filemenu, tearoff=0)
    filemenu.add_cascade(label="Recently accessed", menu=recent_files_menu, accelerator="Alt+R")
    build_recent_files_menu()  # Initialize the recent files menu with loaded files
    
    filemenu.add_command(label="Save")
    filemenu.add_command(label="Exit", command=quit_app)
    
    # Create Edit menu
    editmenu = Menu(menubar)
    menubar.add_cascade(label="Edit", menu=editmenu)
    editmenu.add_command(label="Clear Fields", command=clear_metadata_fields)
    editmenu.add_command(label="Copy All")
    editmenu.add_command(label="Paste All")
    editmenu.add_command(label="Export data", command=export_metadata_to_json)
    
    # Create Help menu
    # Create Help menu
    helpmenu = Menu(menubar)
    menubar.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About", command=show_about_dialog)
    helpmenu.add_command(label="License", command=show_license_dialog)
    helpmenu.add_command(label="Usage Guide", command=open_usage_guide)
    selected_file = None
    
    # Create a main container frame with proper padding
    main_frame = tk.Frame(root, padx=10, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Top frame for buttons and file selection
    top_frame = tk.Frame(main_frame, relief=tk.RAISED, bd=1)
    top_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Create select file button
    # Create select file button
    button_select_file = tk.Button(top_frame, text="Select File", command=select_file, 
                                  padx=10, pady=5)
    button_select_file.pack(side=tk.LEFT, padx=10, pady=8)
    
    # Create navigation buttons for previous and next file
    global nav_prev_button, nav_next_button
    nav_prev_button = tk.Button(top_frame, text="←", command=prev_file, 
                               padx=5, pady=5, state=tk.DISABLED)
    nav_prev_button.pack(side=tk.LEFT, padx=(0, 2), pady=8)
    
    nav_next_button = tk.Button(top_frame, text="→", command=next_file, 
                               padx=5, pady=5, state=tk.DISABLED)
    nav_next_button.pack(side=tk.LEFT, padx=(0, 10), pady=8)
    
    # Create write button
    button_write = tk.Button(top_frame, text="Write Metadata", command=write_metadata,
                            padx=10, pady=5)
    button_write.pack(side=tk.LEFT, padx=10, pady=8)
    # Create filename display label
    filename_label = tk.Label(top_frame, text="No file selected", font=("Arial", 10, "bold"))
    filename_label.pack(side=tk.LEFT, padx=20, pady=8)
    
    # Create a frame for the main content area with two columns
    content_frame = tk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # Create a frame for metadata entry fields (left side)
    metadata_frame = tk.LabelFrame(content_frame, text="Metadata Fields", padx=15, pady=15, font=("Arial", 9, "bold"))
    metadata_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # Create a grid inside the metadata frame for the form fields
    metadata_grid = tk.Frame(metadata_frame)
    metadata_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create labels with consistent styling
    label_style = {"anchor": "e", "padx": 5, "pady": 3, "font": ("Arial", 9)}
    label_headline = tk.Label(metadata_grid, text="Headline:", **label_style)
    label_caption_abstract = tk.Label(metadata_grid, text="Caption Abstract:", **label_style)
    label_credit = tk.Label(metadata_grid, text="Credit:", **label_style)
    label_object_name = tk.Label(metadata_grid, text="Unique ID [Object Name]:", **label_style)
    label_writer_editor = tk.Label(metadata_grid, text="Writer/Editor:", **label_style)
    label_by_line = tk.Label(metadata_grid, text="By-line:", **label_style)
    label_source = tk.Label(metadata_grid, text="Source:", **label_style)
    label_date = tk.Label(metadata_grid, text="Date Created:", **label_style)
    label_copyright_notice = tk.Label(metadata_grid, text="Copyright Notice:", **label_style)
    
    # Create input fields with consistent width
    entry_width = 50
    entry_style = {"width": entry_width, "font": ("Arial", 9)}
    entry_headline = tk.Entry(metadata_grid, **entry_style)
    # Create a frame to hold the Text widget and scrollbar for Caption Abstract
    caption_frame = tk.Frame(metadata_grid)
    
    # Create a scrollbar for the Text widget
    caption_scrollbar = tk.Scrollbar(caption_frame, orient="vertical")
    
    # Create the Text widget with appropriate height, width and scrollbar
    text_caption_abstract = tk.Text(
        caption_frame, 
        height=4,  # Approximately 4 lines
        width=entry_width - 2,  # Slightly less width to account for scrollbar
        wrap=tk.WORD,  # Wrap at word boundaries
        font=("Arial", 9),
        yscrollcommand=caption_scrollbar.set
    )
    
    # Configure the scrollbar to work with the Text widget
    caption_scrollbar.config(command=text_caption_abstract.yview)
    
    # Pack the Text widget and scrollbar in the caption frame
    text_caption_abstract.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    caption_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create a label to display character count
    caption_char_count = tk.Label(
        metadata_grid, 
        text="0/256 characters", 
        font=("Arial", 8), 
        anchor=tk.E
    )
    
    # Function to update character count and limit to 256 characters
    def update_char_count(event=None):
        current_text = text_caption_abstract.get("1.0", "end-1c")
        current_length = len(current_text)
        
        # Update the character count label
        caption_char_count.config(
            text=f"{current_length}/256 characters",
            fg="black" if current_length <= 256 else "red"
        )
        
        # If over the character limit, truncate the text
        if current_length > 256:
            # Delete the current text and reinsert only the first 256 characters
            text_caption_abstract.delete("1.0", tk.END)
            text_caption_abstract.insert("1.0", current_text[:256])
            # Move cursor to the end
            text_caption_abstract.mark_set(tk.INSERT, tk.END)
            
            # Update the character count again after truncation
            caption_char_count.config(text="256/256 characters")
        
        return True
    
    # Bind keyup events to update character count
    text_caption_abstract.bind("<KeyRelease>", update_char_count)
    entry_credit = tk.Entry(metadata_grid, **entry_style)
    entry_object_name = tk.Entry(metadata_grid, **entry_style)
    entry_writer_editor = tk.Entry(metadata_grid, **entry_style)
    entry_by_line = tk.Entry(metadata_grid, **entry_style)
    entry_source = tk.Entry(metadata_grid, **entry_style)
    entry_date = tk.Entry(metadata_grid, **entry_style)
    entry_copyright_notice = tk.Entry(metadata_grid, **entry_style)
    
    # Arrange labels and entries in the grid
    row = 0
    grid_padx = (5, 5)
    grid_pady = 3
    
    label_headline.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_headline.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    row += 1
    
    label_caption_abstract.grid(row=row, column=0, sticky=tk.NE, padx=grid_padx, pady=grid_pady)
    caption_frame.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    caption_char_count.grid(row=row+1, column=1, sticky=tk.E, padx=grid_padx, pady=(0, grid_pady))
    row += 1  # Add an extra row increment for the character count
    row += 1
    
    label_credit.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_credit.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    row += 1
    
    label_object_name.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_object_name.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    row += 1
    
    label_writer_editor.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_writer_editor.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    row += 1
    
    label_by_line.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_by_line.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    row += 1
    
    label_source.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_source.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    row += 1
    
    label_date.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_date.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    row += 1
    
    label_copyright_notice.grid(row=row, column=0, sticky=tk.E, padx=grid_padx, pady=grid_pady)
    entry_copyright_notice.grid(row=row, column=1, sticky=tk.W, padx=grid_padx, pady=grid_pady)
    
    # Create a frame for the thumbnail display (right side)
    thumbnail_frame = tk.LabelFrame(content_frame, text="Image Preview", padx=15, pady=15, font=("Arial", 9, "bold"))
    thumbnail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 0))
    
    # Create a container for the thumbnail with fixed size
    thumbnail_container = tk.Frame(thumbnail_frame, width=220, height=220, bd=1, relief=tk.SUNKEN)
    thumbnail_container.pack(padx=10, pady=10)
    thumbnail_container.pack_propagate(False)  # Prevent the frame from resizing to fit its contents
    
    # Create the thumbnail label inside the container
    # Create the thumbnail label inside the container
    thumbnail_label = tk.Label(thumbnail_container, text="No image to display", bg="light gray", 
                              width=200, height=200)
    thumbnail_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    thumbnail_label.bind("<Button-1>", lambda event: show_full_image())    # Click to show full image
    # Add a button to view the full image
    view_button = tk.Button(thumbnail_frame, text="View Full Image", command=show_full_image,
                           padx=10, pady=5)
    view_button.pack(pady=10)
    
    
    # Create a status bar at the bottom
    status_frame = tk.Frame(main_frame, relief=tk.SUNKEN, bd=1)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Status label on the left
    status_label = tk.Label(status_frame, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=10, pady=5)
    status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Initialize the thumbnail display if a file is selected
    if initial_file:
        select_file(initial_file)
    else:
        # Initialize with empty list of directory image files
        get_directory_image_files()
        update_navigation_buttons()
        
        # Show navigation hint in status bar if there are multiple image files
        if directory_image_files and len(directory_image_files) > 1:
            status_label.config(text=f"Use ← → buttons to navigate through {len(directory_image_files)} images in folder", fg="blue")
    
    root.mainloop()

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Metadata Tag Writer for TIF and JPG images")
    parser.add_argument("file_path", nargs="?", help="Path to the image file to process")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information and exit")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Handle version flag
    # Handle version flag
    if args.version:
        version_text = "tag-writer.py  version .12  (2025-04-04)"
        
        # Add PIL/ImageTk status to version output
        if not PIL_AVAILABLE:
            version_text += " [PIL/Pillow not available]"
        elif not IMAGETK_AVAILABLE:
            version_text += " [ImageTk not available]"
        else:
            version_text += " [Full thumbnail support]"
            
        print(version_text)
        sys.exit(0)
    # Handle file path argument
    if args.file_path:
        try:
            # Log PIL/ImageTk availability status
            if not PIL_AVAILABLE:
                logging.warning("Starting without PIL/Pillow support - thumbnail display disabled")
            elif not IMAGETK_AVAILABLE:
                logging.warning("Starting without ImageTk support - thumbnail display disabled")
            else:
                logging.info("Starting with full thumbnail support")
                
            start_gui(args.file_path)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            sys.exit(1)
    else:
        # No arguments provided, start with GUI only
        # Log PIL/ImageTk availability status
        if not PIL_AVAILABLE:
            logging.warning("Starting without PIL/Pillow support - thumbnail display disabled")
        elif not IMAGETK_AVAILABLE:
            logging.warning("Starting without ImageTk support - thumbnail display disabled")
        else:
            logging.info("Starting with full thumbnail support")
            
        start_gui()
