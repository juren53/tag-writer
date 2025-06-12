#!/usr/bin/python3
#-----------------------------------------------------------
# ############   tag-writer.py  v0.5  ################
# This program creates a GUI interface for entering and    
# writing IPTC metadata tags to TIF and JPG images selected   
# from a directory pick list using the tkinter libraries.
# This program is intended as a free form metadata tagger
# where the photo is not available in the HST PDB
#  Created Sat 01 Jul 2023 07:37:56 AM CDT   [IPTC]
#  Updated Sun 02 Jul 2023 04:53:41 PM CDT added no-backup
#  Updated Sat 29 Mar 2025 07:51:49 PM CDT Updated to use execute_json() for robust metadata retrieval
#  Updated Sat 29 Mar 2025 07:51:49 PM CDT added read existing metadata from file for editing 
#-----------------------------------------------------------

import tkinter as tk
from tkinter import filedialog
from tkinter import Menu
import exiftool

def select_file():
    global selected_file
    selected_file = filedialog.askopenfilename(title="Select")
    read_metadata()  # Read metadata after selecting the file

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

def write_metadata():
    if not selected_file:
        print("No file selected!")
        return

    Headline = entry_headline.get()
    Credit = entry_credit.get()
    ObjectName = entry_object_name.get()
    CaptionAbstract = entry_caption_abstract.get()
    WriterEditor = entry_writer_editor.get()
    By_line = entry_by_line.get()
    Source = entry_source.get()
    Date = entry_date.get()

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

    print("Metadata written successfully!")

# Create the GUI window
root = tk.Tk()
root.title("Metadata Tag Writer")

root.geometry("700x260")     # sets default window size 
    
menubar = Menu(root)
root.config(menu=menubar)

filemenu = Menu(menubar)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Open")
filemenu.add_command(label="Save")
filemenu.add_command(label="Exit")

selected_file = None

# Create select file button
button_select_file = tk.Button(root, text="Select File", command=select_file)
button_select_file.grid(row=0, column=0)

# Create write button
button_write = tk.Button(root, text="Write Metadata", command=write_metadata)
button_write.grid(row=0, column=1)

# Create input fields
entry_headline = tk.Entry(root, width=60)
entry_caption_abstract = tk.Entry(root, width=60)
entry_credit = tk.Entry(root)
entry_object_name = tk.Entry(root)
entry_writer_editor = tk.Entry(root)
entry_by_line = tk.Entry(root)
entry_source = tk.Entry(root)
entry_date = tk.Entry(root)

# Create labels
label_headline = tk.Label(root, justify="left", text="Headline:")
label_caption_abstract = tk.Label(root, text="Caption Abstract:")
label_credit = tk.Label(root, text="Credit:")
label_object_name = tk.Label(root, text="Unique ID [Object Name]: ")
label_writer_editor = tk.Label(root, text="Writer Editor:")
label_by_line = tk.Label(root, text="By-line [photographer]:")
label_source = tk.Label(root, text="Source:")
label_date = tk.Label(root, text="Date Created [YYY-MM-DD]:")

# Grid layout
label_headline.grid(row=1, column=0, sticky="w")
entry_headline.grid(row=1, column=1, sticky="w")

label_credit.grid(row=2, column=0, sticky="w")
entry_credit.grid(row=2, column=1, sticky="w")

label_object_name.grid(row=3, column=0, sticky="w")
entry_object_name.grid(row=3, column=1, sticky="w")

label_caption_abstract.grid(row=4, column=0, sticky="w")
entry_caption_abstract.grid(row=4, column=1, sticky="w")

label_writer_editor.grid(row=5, column=0, sticky="w")
entry_writer_editor.grid(row=5, column=1, sticky="w")

label_by_line.grid(row=6, column=0, sticky="w")
entry_by_line.grid(row=6, column=1, sticky="w")

label_source.grid(row=7, column=0, sticky="w")
entry_source.grid(row=7, column=1, sticky="w")

label_date.grid(row=8, column=0, sticky="w")
entry_date.grid(row=8, column=1, sticky="w")

# message lower right filename, version and date
label = tk.Label(root, text="tag-writer.py   ver 0.5   2023-10-30   ", bg="lightgray")
label.grid(row=10, columnspan=2, sticky="se")

root.mainloop()
