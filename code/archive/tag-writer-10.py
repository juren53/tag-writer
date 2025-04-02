#!/usr/bin/python3
#-----------------------------------------------------------
# ############   tag-writer.py  Ver 0.10  ################
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
#-----------------------------------------------------------

import tkinter as tk
from tkinter import filedialog
from tkinter import Menu
from tkinter import messagebox
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
    if os.path.isfile(file_path):
        select_file(file_path)
    else:
        # If the file no longer exists, show an error and update the menu
        global status_label
        if 'status_label' in globals() and status_label:
            status_label.config(text=f"Error: File '{os.path.basename(file_path)}' no longer exists", fg="red")
        if file_path in recent_files:
            recent_files.remove(file_path)
            build_recent_files_menu()

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

def select_file(file_path=None):
    global selected_file, filename_label
    if file_path:
        if os.path.isfile(file_path):
            selected_file = file_path
            # Update the filename label if it exists
            if 'filename_label' in globals() and filename_label:
                filename_label.config(text=f"File: {os.path.basename(selected_file)}")
            read_metadata()  # Read metadata after selecting the file
            update_thumbnail()  # Update the thumbnail display
            update_recent_files(file_path)  # Update the recent files list
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
    
    entry_caption_abstract.delete(0, tk.END)
    entry_caption_abstract.insert(0, safe_get(metadata, 'Caption-Abstract'))
    
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
    CaptionAbstract = entry_caption_abstract.get()
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
    entry_caption_abstract.delete(0, tk.END)
    entry_credit.delete(0, tk.END)
    entry_object_name.delete(0, tk.END)
    entry_writer_editor.delete(0, tk.END)
    entry_by_line.delete(0, tk.END)
    entry_source.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    entry_copyright_notice.delete(0, tk.END)
    
    # Update status label
    status_label.config(text="All fields cleared", fg="green")

def update_version_label_position(event=None):
    """Update the position of the version label to stay in the bottom right corner."""
    global version_label, root
    # Place the label at bottom right with a small margin
    version_label.place(x=root.winfo_width() - version_label.winfo_reqwidth() - 5, 
                       y=root.winfo_height() - version_label.winfo_reqheight() - 5)

def update_thumbnail():
    """Load the selected image file and display it as a thumbnail with robust error handling."""
    global selected_file, thumbnail_label, thumbnail_image
    
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
            # Print image info for debugging
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
        
        # Store original image for comparison
        original_img = img.copy()
        
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

def show_full_image():
    """
    Displays the full-sized version of the currently selected image in a new window.
    
    Features:
    - Creates a new Toplevel window with the image filename as part of the title
    - Loads the full image using PIL/Pillow, scaling down if too large for the screen
    - Displays a button to close the window
    - Handles potential errors gracefully with appropriate user feedback
    """
    global selected_file, root
    
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
        
        # Calculate the scaling factor if image is too large
        scale_width = max_width / original_width if original_width > max_width else 1
        scale_height = max_height / original_height if original_height > max_height else 1
        scale = min(scale_width, scale_height)
        
        # Resize image if necessary
        if scale < 1:
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # Use appropriate resampling method based on PIL version
            try:
                img = img.resize((new_width, new_height), Image.LANCZOS)
            except AttributeError:
                try:
                    img = img.resize((new_width, new_height), Image.ANTIALIAS)
                except AttributeError:
                    img = img.resize((new_width, new_height))
        
        # Convert to PhotoImage for display
        if IMAGETK_AVAILABLE:
            photo_img = ImageTk.PhotoImage(img)
            
            # Create label to display the image
            image_label = tk.Label(img_window, image=photo_img)
            image_label.image = photo_img  # Keep a reference
            image_label.pack(padx=10, pady=10)
            
            # Add dimension information
            if scale < 1:
                info_text = f"Scaled image: {photo_img.width()}x{photo_img.height()} (Original: {original_width}x{original_height})"
            else:
                info_text = f"Original size: {original_width}x{original_height}"
            
            info_label = tk.Label(img_window, text=info_text)
            info_label.pack(pady=5)
            
            # Add close button
            close_button = tk.Button(img_window, text="Close", command=img_window.destroy)
            close_button.pack(pady=10)
            # Set focus to window
            img_window.focus_set()
            
            # Bind Escape key to close the window
            img_window.bind("<Escape>", lambda e: img_window.destroy())
            
            # Update the window to ensure it's rendered before attempting to grab
            img_window.update()
            
            # Set grab after a short delay to ensure window is visible
            def set_grab():
                try:
                    if img_window.winfo_exists():
                        img_window.grab_set()
                except Exception as e:
                    logging.error(f"Error setting grab on image window: {str(e)}")
                    
            # Schedule grab_set to occur after the window is fully visible
            img_window.after(100, set_grab)
        else:
            # Handle case where ImageTk is not available
            img_window.geometry("400x150")
            error_label = tk.Label(img_window, 
                                  text="ImageTk is not available.\nCannot display the full image.",
                                  fg="red")
            error_label.pack(padx=20, pady=20)
            
            # Add close button
            close_button = tk.Button(img_window, text="Close", command=img_window.destroy)
            close_button.pack(pady=10)
    
    except Exception as e:
        # Handle any errors that might occur
        if 'img_window' in locals() and img_window.winfo_exists():
            img_window.destroy()  # Close the window if it exists
        
        error_message = f"Error displaying image: {str(e)}"
        logging.error(error_message)
        messagebox.showerror("Error", error_message)


def start_gui(initial_file=None):
    global root, entry_headline, entry_caption_abstract, entry_credit, entry_object_name
    global entry_writer_editor, entry_by_line, entry_source, entry_date, entry_copyright_notice, selected_file
    global status_label, filename_label, version_label, thumbnail_label, thumbnail_image, recent_files_menu
    # Create the GUI window
    root = tk.Tk()
    root.title("Metadata Tag Writer")
    
    root.geometry("1000x400")     # sets default window size
    
    # Load recent files from config file
    load_recent_files()
    
    # Add function to exit application when 'q' is pressed
    def quit_app(event=None):
        save_recent_files()  # Save recent files before closing
        root.destroy()
    
    # Bind the 'q' key to the quit_app function
    root.bind('<q>', quit_app)
    
    # Function to show About dialog
    def show_about_dialog():
        messagebox.showinfo(
            "About Tag Writer",
            "Tag Writer\n\n"
            "Version: 0.10\n\n"
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
        license_text = """tag-writer


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
    filemenu.add_cascade(label="Recently accessed", menu=recent_files_menu)
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
    
    # Create select file button
    button_select_file = tk.Button(root, text="Select File", command=select_file)
    button_select_file.grid(row=0, column=1)
    
    # Create write button
    button_write = tk.Button(root, text="Write Metadata", command=write_metadata)
    button_write.grid(row=0, column=2)
    
    # Create filename display label
    filename_label = tk.Label(root, text="No file selected", font=("Arial", 10, "bold"))
    filename_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    # Create input fields
    entry_headline = tk.Entry(root, width=60)
    entry_caption_abstract = tk.Entry(root, width=60)
    entry_credit = tk.Entry(root)
    entry_object_name = tk.Entry(root)
    entry_writer_editor = tk.Entry(root)
    entry_by_line = tk.Entry(root)
    entry_source = tk.Entry(root)
    entry_date = tk.Entry(root)
    entry_copyright_notice = tk.Entry(root)
    
    # Create labels
    label_headline = tk.Label(root, justify="left", text="Headline:")
    label_caption_abstract = tk.Label(root, text="Caption Abstract:")
    label_credit = tk.Label(root, text="Credit:")
    label_object_name = tk.Label(root, text="Unique ID [Object Name]: ")
    label_writer_editor = tk.Label(root, text="Writer Editor:")
    label_by_line = tk.Label(root, text="By-line [photographer]:")
    label_source = tk.Label(root, text="Source:")
    label_date = tk.Label(root, text="Date Created [YYY-MM-DD]:")
    label_copyright_notice = tk.Label(root, text="Copyright Notice:")
    
    # Grid layout
    label_headline.grid(row=2, column=0, sticky="w")
    entry_headline.grid(row=2, column=1, sticky="w")
    
    label_credit.grid(row=3, column=0, sticky="w")
    entry_credit.grid(row=3, column=1, sticky="w")
    
    label_object_name.grid(row=4, column=0, sticky="w")
    entry_object_name.grid(row=4, column=1, sticky="w")
    
    label_caption_abstract.grid(row=5, column=0, sticky="w")
    entry_caption_abstract.grid(row=5, column=1, sticky="w")
    
    label_writer_editor.grid(row=6, column=0, sticky="w")
    entry_writer_editor.grid(row=6, column=1, sticky="w")
    
    label_by_line.grid(row=7, column=0, sticky="w")
    entry_by_line.grid(row=7, column=1, sticky="w")
    
    label_source.grid(row=8, column=0, sticky="w")
    entry_source.grid(row=8, column=1, sticky="w")
    
    label_date.grid(row=9, column=0, sticky="w")
    entry_date.grid(row=9, column=1, sticky="w")
    
    label_copyright_notice.grid(row=10, column=0, sticky="w")
    entry_copyright_notice.grid(row=10, column=1, sticky="w")
    
    # Status message label
    status_label = tk.Label(root, text="", fg="green")
    status_label.grid(row=11, columnspan=2, sticky="w")
    
    # Create and configure the thumbnail display area
    # Create a frame with fixed size for thumbnail display
    thumbnail_frame = tk.Frame(root, width=220, height=220, relief=tk.SUNKEN, borderwidth=1)
    thumbnail_frame.grid(row=2, column=2, rowspan=9, padx=10, pady=5, sticky="ne")
    # Prevent the frame from shrinking to fit its contents
    thumbnail_frame.grid_propagate(False)
    # Make sure the frame expands within its cell
    thumbnail_frame.columnconfigure(0, weight=1)
    thumbnail_frame.rowconfigure(0, weight=1)
    
    # Place holder for thumbnail image
    thumbnail_image = None
    
    # Adjust the thumbnail label based on PIL/ImageTk availability
    if PIL_AVAILABLE and IMAGETK_AVAILABLE:
        thumbnail_status = "No image to display"
    elif PIL_AVAILABLE and not IMAGETK_AVAILABLE:
        thumbnail_status = "ImageTk not available\nCannot display thumbnails"
    else:
        thumbnail_status = "PIL/Pillow not available\nCannot display thumbnails"
    
    logging.debug(f"Creating thumbnail_label with status: {thumbnail_status}")
    # Create label with appropriate minimal size to display a 200x157 image
    thumbnail_label = tk.Label(thumbnail_frame, text=thumbnail_status, 
                              width=200, height=157,  # Set minimum width/height in pixels
                              compound=tk.TOP,  # Position image at the top, text below
                              anchor=tk.CENTER,  # Center the content
                              relief=tk.FLAT,
                              cursor="hand2",  # Set cursor to hand to indicate clickability
                              padx=5, pady=5)  # Add padding inside the label
    # Position the label to fill the entire frame
    thumbnail_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    # Bind click event to show full image when thumbnail is clicked
    thumbnail_label.bind("<Button-1>", lambda event: show_full_image())
    
    # Log information about the thumbnail label
    logging.debug(f"thumbnail_label created with initial dimensions: {thumbnail_label.winfo_reqwidth()}x{thumbnail_label.winfo_reqheight()}")
    print(f"DEBUG: Thumbnail label created with dimensions: {thumbnail_label.winfo_reqwidth()}x{thumbnail_label.winfo_reqheight()}")
    
    # Add indicator about PIL status
    if not PIL_AVAILABLE or not IMAGETK_AVAILABLE:
        status_frame = tk.Frame(thumbnail_frame)
        status_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        
        # Use Unicode symbols for indicators
        status_icon = "⚠️" if not PIL_AVAILABLE else "ℹ️"
        status_text = "PIL missing" if not PIL_AVAILABLE else "ImageTk missing"
        
        status_indicator = tk.Label(status_frame, text=f"{status_icon} {status_text}", 
                                   fg="red" if not PIL_AVAILABLE else "orange",
                                   font=("Arial", 8))
        status_indicator.grid(row=0, column=0, pady=2)
    
    # Create version label that will be positioned dynamically
    version_text = "tag-writer.py   ver .10  2025-04-02   "
    # Add PIL status to version label
    if not PIL_AVAILABLE:
        version_text += " [PIL missing]"
    elif not IMAGETK_AVAILABLE:
        version_text += " [ImageTk missing]"
    
    version_label = tk.Label(root, text=version_text, bg="lightgray")
    
    # Bind resize event to update the version label position
    root.bind("<Configure>", update_version_label_position)
    
    # If an initial file was provided, select it
    if initial_file:
        select_file(initial_file)
    else:
        filename_label.config(text="No file selected")
    
    # Call once to position the version label after window is fully created
    # We use after() to ensure the window is fully rendered
    root.update_idletasks()
    root.after(100, update_version_label_position)
    
    # Initialize the thumbnail display if a file is selected
    if initial_file:
        update_thumbnail()
    
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
        version_text = "tag-writer.py  version .10  (2025-04-02)"
        
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
