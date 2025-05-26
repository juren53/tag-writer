#!/usr/bin/python3
#-----------------------------------------------------------
# ############   tag-writer-wx.py  Ver 0.04d ################
# This program creates a GUI interface for entering and    
# writing IPTC metadata tags to TIF and JPG images selected   
# from a directory pick list using wxPython libraries.
# This program is intended as a free form metadata tagger
# when metada can not be pulled from an online database. 
#  Created Sat 01 Jul 2023 07:37:56 AM CDT   [IPTC]
#  Updated Sat 05 Apr 2025 11:24:00 PM CDT Converted from tkinter to wxPython
#  Updated Sun 13 Apr 2025 10:20:00 AM CDT v 0.04 c Load last image on startup
#  Updated Sun 13 Apr 2025 12:44:00 AM CDT v 0.04 d Key board arrow keys scroll through CWD
#-----------------------------------------------------------

import wx
import wx.adv
import exiftool
import argparse
import os
import sys
import io
import logging
import json
import webbrowser
from pathlib import Path

# Global list to store recently accessed files (max 5)
recent_files = []
# Global variables for full image preview zoom functionality
original_image = None
full_image_original = None
full_image_zoom_factor = 1.0
# Global variables for directory navigation
directory_image_files = []
current_file_index = -1
# Config file for storing persistent data
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".tag_writer_config.json")
# Global flag to suppress LibTIFF warnings
SUPPRESS_LIBTIFF_WARNINGS = True
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom context manager to suppress stderr output
class SuppressStderr:
    """Context manager to suppress stderr output"""
    def __init__(self):
        self.stderr = None
        self.devnull = None

    def __enter__(self):
        if SUPPRESS_LIBTIFF_WARNINGS:
            self.stderr = sys.stderr
            self.devnull = open(os.devnull, 'w')
            sys.stderr = self.devnull
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if SUPPRESS_LIBTIFF_WARNINGS and self.stderr:
            sys.stderr = self.stderr
            self.devnull.close()

# Global helper functions
def is_richtiffiptc_warning(warning_text):
    """Check if a warning message is related to RichTIFFIPTC and should be suppressed from UI"""
    if not warning_text:
        return False
    
    # List of warning patterns to suppress
    suppress_patterns = [
        "RichTIFFIPTC",
        "TIFFFetchNormalTag",
        "Incorrect value"
    ]
    
    # Check if any of the patterns are in the warning
    for pattern in suppress_patterns:
        if pattern in warning_text:
            return True
    
    return False

# Global variable for the selected file
selected_file = None

# Try to import PIL/Pillow components with fallback options
PIL_AVAILABLE = False
try:
    from PIL import Image
    PIL_AVAILABLE = True
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
    global recent_files
    
    # Only add valid files to recent_files list
    if file_path and os.path.isfile(file_path):
        # Remove the file if it's already in the list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add the file to the beginning of the list
        recent_files.insert(0, file_path)
        
        # Limit the list to 5 items
        recent_files = recent_files[:5]

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
    global directory_image_files, selected_file
    
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

def get_metadata(file_path):
    """Retrieve metadata from the specified file using execute_json() method."""
    with exiftool.ExifTool() as et:
        # Use execute_json to get metadata in JSON format with a simpler approach
        # that works better with TIFF files
        try:
            # Check if the file is a TIFF file
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in ['.tif', '.tiff']:
                # Add -m flag for TIFF files to ignore minor errors like RichTIFFIPTC issues
                # Also add -ignoreMinorErrors flag for TIFF files to further suppress warnings
                logging.debug(f"Processing TIFF file with -m flag: {file_path}")
                metadata_json = et.execute_json("-j", "-m", "-ignoreMinorErrors", file_path)
            else:
                metadata_json = et.execute_json("-j", file_path)
            
            # metadata_json returns a list of dictionaries, with one dict per file
            # Since we're only processing one file, we take the first element
            if metadata_json and len(metadata_json) > 0:
                raw_metadata = metadata_json[0]
                return process_metadata(raw_metadata)
            else:
                logging.warning("No metadata found or empty metadata returned")
                return {}
        except Exception as e:
            # Enhanced error handling to provide more information for troubleshooting
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in ['.tif', '.tiff']:
                logging.error(f"Error processing TIFF file with exiftool: {str(e)}")
                # Log additional details that might help diagnose the issue
                logging.debug(f"TIFF file path: {file_path}")
                logging.debug(f"File exists: {os.path.exists(file_path)}")
                logging.debug(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'}")
                
                # Try again with additional options if first attempt failed
                try:
                    logging.warning(f"Retrying TIFF file with additional options: {file_path}")
                    # Try with both -m and -fast flags as a last resort
                    metadata_json = et.execute_json("-j", "-m", "-fast", file_path)
                    if metadata_json and len(metadata_json) > 0:
                        logging.info(f"Successfully retrieved metadata on second attempt for: {file_path}")
                        return process_metadata(metadata_json[0])
                except Exception as retry_error:
                    logging.error(f"Second attempt failed for TIFF file: {str(retry_error)}")
            else:
                logging.error(f"Error executing exiftool: {str(e)}")
            return {}

# Helper function to process metadata after extraction
def process_metadata(raw_metadata):
    """Process raw metadata to standardize field names."""
    metadata = {}
    
    # Filter out RichTIFFIPTC warnings if present
    if 'ExifTool:Warning' in raw_metadata:
        warning = raw_metadata['ExifTool:Warning']
        # Check if it's a list or a single string
        if isinstance(warning, list):
            # Filter out RichTIFFIPTC and related warnings from the list
            filtered_warnings = [w for w in warning if not is_richtiffiptc_warning(w)]
            if filtered_warnings:
                raw_metadata['ExifTool:Warning'] = filtered_warnings
            else:
                # If all warnings were suppressed, remove the warning entirely
                del raw_metadata['ExifTool:Warning']
        elif isinstance(warning, str) and is_richtiffiptc_warning(warning):
            # If the only warning is about RichTIFFIPTC or related issues, remove it
            del raw_metadata['ExifTool:Warning']
    
    # Define mappings for IPTC field names to possible ExifTool field names
    field_mappings = {
        'Headline': ['IPTC:Headline', 'XMP-photoshop:Headline', 'XMP:Headline', 'XMP:Title'],
        'Caption-Abstract': ['IPTC:Caption-Abstract', 'XMP:Description', 'EXIF:ImageDescription'],
        'Credit': ['IPTC:Credit', 'XMP:Credit', 'XMP-photoshop:Credit'],
        'Object Name': ['IPTC:ObjectName', 'IPTC:Object Name', 'XMP:Title'],
        'Writer-Editor': ['IPTC:Writer-Editor', 'XMP:CaptionWriter', 'XMP-photoshop:CaptionWriter'],
        'By-line': ['IPTC:By-line', 'XMP:Creator', 'EXIF:Artist'],
        'Source': ['IPTC:Source', 'XMP:Source', 'XMP-photoshop:Source'],
        'Date Created': ['IPTC:DateCreated', 'XMP:DateCreated', 'XMP-photoshop:DateCreated'],
        'Copyright Notice': ['IPTC:CopyrightNotice', 'XMP:Rights', 'EXIF:Copyright']
    }
    
    # Log raw metadata field names for debugging
    logging.debug(f"Raw metadata fields: {list(raw_metadata.keys())}")
    
    # Map the fields
    for field, possible_names in field_mappings.items():
        for name in possible_names:
            if name in raw_metadata:
                metadata[field] = raw_metadata[name]
                logging.debug(f"Found '{field}' in '{name}': {raw_metadata[name]}")
                break
    
    # Add debugging log for metadata fields found
    logging.debug(f"Standardized metadata fields found: {list(metadata.keys())}")
    logging.debug(f"Metadata values: {metadata}")
    
    # For backward compatibility, add raw metadata fields as well
    # to allow access to any fields not in our mapping
    metadata.update(raw_metadata)
    
    return metadata

class TagWriterApp(wx.App):
    """Main application class for Tag Writer"""
    def OnInit(self):
        """Initialize the application"""
        # Load preferences if needed
        # self.load_preferences()  # Uncomment if you implement this method
        self.frame = TagWriterFrame(None, title="Metadata Tag Writer")
        self.frame.Show()
        self.SetTopWindow(self.frame)
        
        # Parse command line arguments
        args = parse_arguments()
        
        # Handle version flag
        if args.version:
            version_text = "tag-writer-wx.py  version .04c  (2025-04-13)"
            # Add PIL status to version output
            if not PIL_AVAILABLE:
                version_text += " [PIL/Pillow not available]"
            else:
                version_text += " [PIL support available]"
                
            print(version_text)
            wx.GetApp().ExitMainLoop()
            return False  # Exit the application
        
        # Handle file path argument (command line takes precedence)
        if args.file_path:
            self.frame.select_file(args.file_path)
        # Otherwise, load the most recent file if available
        elif recent_files and len(recent_files) > 0:
            most_recent_file = recent_files[0]
            if os.path.exists(most_recent_file):
                logging.info(f"Loading most recent file: {most_recent_file}")
                self.frame.select_file(most_recent_file)
            else:
                logging.warning(f"Most recent file no longer exists: {most_recent_file}")
        
        return True

# Save application preferences to config
def save_preferences():
    """Save application preferences to config file"""
    global SUPPRESS_LIBTIFF_WARNINGS
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = {}
            
        # Add preferences to config data
        if 'preferences' not in config_data:
            config_data['preferences'] = {}
            
        config_data['preferences']['suppress_libtiff_warnings'] = SUPPRESS_LIBTIFF_WARNINGS
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f)
        logging.debug(f"Preferences saved to {CONFIG_FILE}")
    except Exception as e:
        logging.error(f"Error saving preferences: {str(e)}")
        return False
    return True

class TagWriterFrame(wx.Frame):
    """Main application frame."""
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000, 600))
        
        # Set up class variables
        self.selected_file = None
        self.selected_file = None
        self.filename_label = None
        self.status_label = None
        self.nav_next_button = None
        self.thumbnail_image = None
        self.thumbnail_panel = None
        self.zoom_info_label = None
        self.recent_files_menu = None
        self.metadata = {}
        self.preview_dialog = None
        
        # Entry fields
        self.entry_headline = None
        self.text_caption_abstract = None
        self.entry_credit = None
        self.entry_object_name = None
        self.entry_writer_editor = None
        self.entry_by_line = None
        self.entry_source = None
        self.entry_date = None
        self.entry_copyright_notice = None
        self.caption_char_count = None
        
        # Load recent files
        load_recent_files()
        
        # Set up icons
        self.setup_icons()
        
        # Create the UI layout
        self.create_ui()
        
        # Set up key shortcuts
        self.setup_accelerators()
        
        # Set up events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        # Set focus to the panel to enable keyboard navigation
        # Use CallAfter to ensure focus is set after all initialization is complete
        wx.CallAfter(self.panel.SetFocusIgnoringChildren)
    
    def setup_icons(self):
        """Set up application icons"""
        try:
            if PIL_AVAILABLE:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ICON_tw.png")
                if os.path.exists(icon_path):
                    icon = wx.Icon(icon_path)
                    self.SetIcon(icon)
                    logging.info(f"Successfully set application icon from {icon_path}")
                else:
                    logging.warning(f"Icon file not found: {icon_path}")
        except Exception as e:
            logging.error(f"Error setting application icon: {str(e)}")
    
    def create_ui(self):
        """Create the user interface"""
        # Create the main panel
        self.panel = wx.Panel(self)
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Create the status bar
        self.create_status_bar()
        
        
        # Create the main layout
        self.create_layout()
        
        # Bind key events to all input controls for better keyboard navigation
        self.entry_headline.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.text_caption_abstract.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.entry_credit.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.entry_object_name.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.entry_writer_editor.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.entry_by_line.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.entry_date.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.entry_copyright_notice.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # Set focus handling for keyboard navigation
        self.panel.SetFocus()
        self.panel.Bind(wx.EVT_SET_FOCUS, self.on_panel_focus)
        self.Bind(wx.EVT_ACTIVATE, self.on_window_activate)
    
    def on_panel_focus(self, event):
        """Handle panel focus events"""
        event.Skip()  # Allow focus to propagate

    def on_window_activate(self, event):
        """Handle window activation"""
        if event.GetActive():
            # When window becomes active, set focus to panel for keyboard navigation
            wx.CallAfter(self.panel.SetFocus)
        event.Skip()
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        # Create menubar
        menubar = wx.MenuBar()
        
        # File menu
        filemenu = wx.Menu()
        item_open = filemenu.Append(wx.ID_OPEN, "&Open", "Open an image file")
        
        # Recent files submenu
        self.recent_files_menu = wx.Menu()
        filemenu.AppendSubMenu(self.recent_files_menu, "Recently accessed\tAlt+R")
        self.build_recent_files_menu()
        
        filemenu.AppendSeparator()
        item_exit = filemenu.Append(wx.ID_EXIT, "E&xit", "Exit the application")
        
        # Edit menu
        editmenu = wx.Menu()
        item_clear = editmenu.Append(wx.ID_CLEAR, "Clear Fields", "Clear all input fields")
        editmenu.AppendSeparator()
        item_export = editmenu.Append(wx.ID_ANY, "Export data", "Export metadata to JSON")
        
        # Help menu
        helpmenu = wx.Menu()
        item_about = helpmenu.Append(wx.ID_ABOUT, "&About", "About Tag Writer")
        item_license = helpmenu.Append(wx.ID_ANY, "&License", "License information")
        item_guide = helpmenu.Append(wx.ID_HELP, "Usage &Guide", "Open usage guide in web browser")
        
        # Add menus to menubar
        menubar.Append(filemenu, "&File")
        menubar.Append(editmenu, "&Edit")
        menubar.Append(helpmenu, "&Help")
        self.SetMenuBar(menubar)
        
        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_open, item_open)
        self.Bind(wx.EVT_MENU, self.on_exit, item_exit)
        self.Bind(wx.EVT_MENU, self.on_clear_fields, item_clear)
        self.Bind(wx.EVT_MENU, self.on_export_data, item_export)
        self.Bind(wx.EVT_MENU, self.on_about, item_about)
        self.Bind(wx.EVT_MENU, self.on_license, item_license)
        self.Bind(wx.EVT_MENU, self.on_usage_guide, item_guide)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.statusbar = self.CreateStatusBar(3)
        self.statusbar.SetStatusWidths([200, -1, 200])
        self.SetStatusText("Ready", 0)
        self.SetStatusText("", 1)  # Middle section for file path
        self.SetStatusText("Ver 0.04d (2025-04-13)", 2)
    
    def create_layout(self):
        """Create the main application layout"""
        # Create main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Top panel for buttons and file display
        top_panel = wx.Panel(self.panel)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # File selection button
        self.btn_select_file = wx.Button(top_panel, label="Select File")
        self.btn_select_file.Bind(wx.EVT_BUTTON, self.on_open)
        top_sizer.Add(self.btn_select_file, 0, wx.ALL, 5)
        
        # Navigation buttons
        self.nav_prev_button = wx.Button(top_panel, label="←", size=(30, -1))
        self.nav_prev_button.Bind(wx.EVT_BUTTON, lambda evt: self.navigate_to_file(-1))
        self.nav_prev_button.Disable()
        top_sizer.Add(self.nav_prev_button, 0, wx.ALL, 5)
        
        self.nav_next_button = wx.Button(top_panel, label="→", size=(30, -1))
        self.nav_next_button.Bind(wx.EVT_BUTTON, lambda evt: self.navigate_to_file(1))
        self.nav_next_button.Disable()
        top_sizer.Add(self.nav_next_button, 0, wx.ALL, 5)
        
        # Write metadata button
        self.btn_write = wx.Button(top_panel, label="Write Metadata")
        self.btn_write.Bind(wx.EVT_BUTTON, self.on_write_metadata)
        top_sizer.Add(self.btn_write, 0, wx.ALL, 5)
        
        # Filename display
        filename_panel = wx.Panel(top_panel)
        filename_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Main filename label (bold)
        self.filename_label = wx.StaticText(filename_panel, label="No file selected")
        self.filename_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        filename_sizer.Add(self.filename_label, 1, wx.ALIGN_CENTER_VERTICAL)
        
        filename_panel.SetSizer(filename_sizer)
        top_sizer.Add(filename_panel, 1, wx.ALL | wx.EXPAND, 10)
        
        top_panel.SetSizer(top_sizer)
        main_sizer.Add(top_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        # Content sizer (metadata and thumbnail)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Metadata panel (left side)
        metadata_panel = wx.Panel(self.panel)
        metadata_box = wx.StaticBox(metadata_panel, label="Metadata Fields")
        metadata_sizer = wx.StaticBoxSizer(metadata_box, wx.VERTICAL)
        
        # Create metadata fields using GridBagSizer for precise control
        fields_sizer = wx.GridBagSizer(5, 5)
        
        # Headline
        row = 0
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Headline:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_headline = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_headline, pos=(row, 1), flag=wx.EXPAND)
        
        # Caption Abstract (multiline text)
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Caption Abstract:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_TOP, border=5)
        
        # Create TextCtrl with scrollbar in a panel
        caption_panel = wx.Panel(metadata_panel)
        caption_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text_caption_abstract = wx.TextCtrl(caption_panel, size=(400, 100), 
                                              style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        caption_sizer.Add(self.text_caption_abstract, 1, wx.EXPAND)
        
        # Character count label
        self.caption_char_count = wx.StaticText(caption_panel, label="0/256 characters")
        self.caption_char_count.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        caption_sizer.Add(self.caption_char_count, 0, wx.ALIGN_RIGHT | wx.TOP, 2)
        
        caption_panel.SetSizer(caption_sizer)
        fields_sizer.Add(caption_panel, pos=(row, 1), flag=wx.EXPAND)
        
        # Bind event to update character count
        self.text_caption_abstract.Bind(wx.EVT_TEXT, self.update_char_count)
        
        # Credit
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Credit:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_credit = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_credit, pos=(row, 1), flag=wx.EXPAND)
        
        # Object Name
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Object Name:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_object_name = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_object_name, pos=(row, 1), flag=wx.EXPAND)
        
        # Writer/Editor
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Writer/Editor:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_writer_editor = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_writer_editor, pos=(row, 1), flag=wx.EXPAND)
        
        # By-line
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="By-line:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_by_line = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_by_line, pos=(row, 1), flag=wx.EXPAND)
        
        # Source
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Source:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_source = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_source, pos=(row, 1), flag=wx.EXPAND)
        
        # Date Created
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Date Created:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_date = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_date, pos=(row, 1), flag=wx.EXPAND)
        
        # Copyright Notice
        row += 1
        fields_sizer.Add(wx.StaticText(metadata_panel, label="Copyright Notice:"), 
                         pos=(row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.entry_copyright_notice = wx.TextCtrl(metadata_panel, size=(400, -1))
        fields_sizer.Add(self.entry_copyright_notice, pos=(row, 1), flag=wx.EXPAND)
        
        # Add some padding to the grid
        fields_sizer.AddGrowableCol(1)
        metadata_sizer.Add(fields_sizer, 1, wx.EXPAND | wx.ALL, 10)
        metadata_panel.SetSizer(metadata_sizer)
        
        # Thumbnail panel (right side)
        thumbnail_panel = wx.Panel(self.panel)
        thumbnail_box = wx.StaticBox(thumbnail_panel, label="Image Preview")
        thumbnail_sizer = wx.StaticBoxSizer(thumbnail_box, wx.VERTICAL)
        
        # Create a fixed-size panel for the thumbnail
        self.thumbnail_panel = wx.Panel(thumbnail_panel, size=(220, 220), style=wx.BORDER_SUNKEN)
        self.thumbnail_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Initialize with "No image" text
        self.thumbnail_text = wx.StaticText(self.thumbnail_panel, label="No image to display",
                                          style=wx.ALIGN_CENTER)
        self.thumbnail_text.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.thumbnail_text.SetForegroundColour(wx.Colour(100, 100, 100))
        
        # Center the text in the thumbnail panel
        thumbnail_text_sizer = wx.BoxSizer(wx.VERTICAL)
        thumbnail_text_sizer.Add(self.thumbnail_text, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        self.thumbnail_panel.SetSizer(thumbnail_text_sizer)
        
        # Add thumbnail panel to its container
        thumbnail_sizer.Add(self.thumbnail_panel, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # View full image button
        self.btn_view_full = wx.Button(thumbnail_panel, label="View Full Image")
        self.btn_view_full.Bind(wx.EVT_BUTTON, self.on_view_full_image)
        thumbnail_sizer.Add(self.btn_view_full, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        # Bind click on thumbnail to view full image
        self.thumbnail_panel.Bind(wx.EVT_LEFT_DOWN, self.on_view_full_image)
        
        thumbnail_panel.SetSizer(thumbnail_sizer)
        
        # Add metadata and thumbnail panels to content sizer
        content_sizer.Add(metadata_panel, 1, wx.EXPAND | wx.RIGHT, 10)
        content_sizer.Add(thumbnail_panel, 0, wx.EXPAND)
        
        # Add content sizer to main sizer
        main_sizer.Add(content_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        # Set up the panel sizer
        self.panel.SetSizer(main_sizer)
        
        # Layout and fit
        main_sizer.Fit(self.panel)
    
    def setup_accelerators(self):
        """Set up keyboard shortcuts"""
        # Update display to show warnings if present (but don't block operation)
        if 'ExifTool:Warning' in self.metadata:
            warning = self.metadata['ExifTool:Warning']
            # Handle different warning formats
            if isinstance(warning, str):
                # Check if this is a warning we should suppress
                if is_richtiffiptc_warning(warning):
                    # Just log it but don't show popup
                    logging.info(f"Suppressed warning: {warning}")
                else:
                    # Show other warnings
                    logging.warning(f"ExifTool Warning: {warning}")
                    wx.MessageBox(warning, "ExifTool Warning", wx.OK | wx.ICON_WARNING)
            elif isinstance(warning, list):
                # Filter warnings to show (exclude suppressed warning types)
                warnings_to_show = [w for w in warning if not is_richtiffiptc_warning(w)]
                
                # Log the suppressed warnings
                suppressed_warnings = [w for w in warning if is_richtiffiptc_warning(w)]
                if suppressed_warnings:
                    logging.info(f"Suppressed warnings: {suppressed_warnings}")
                
                # Show only non-suppressed warnings
                if warnings_to_show:
                    combined_warning = "\n".join(warnings_to_show)
                    logging.warning(f"ExifTool Warning: {combined_warning}")
                    wx.MessageBox(combined_warning, "ExifTool Warning", wx.OK | wx.ICON_WARNING)
        
        # Create an accelerator table for keyboard shortcuts
        accel_entries = [
            # File menu
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('O'), wx.ID_OPEN),  # Ctrl+O for Open
            # Edit menu
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('L'), wx.ID_CLEAR),  # Ctrl+L for Clear fields
            # We don't add LEFT/RIGHT here because accelerator tables don't work well with them
        ]
        
        accel_tbl = wx.AcceleratorTable(accel_entries)
        self.SetAcceleratorTable(accel_tbl)
        
        # Bind key events for navigation (left/right arrows)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # Also bind to the panel to ensure it catches key events when focused
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # Ensure the panel can receive keyboard focus
        self.panel.SetFocusIgnoringChildren()
    def build_recent_files_menu(self):
        """Build the recent files menu"""
        global recent_files
        
        # Clear the menu by removing all existing items
        menu_items = self.recent_files_menu.GetMenuItems()
        for item in menu_items:
            self.recent_files_menu.Remove(item.GetId())
        
        # Add recent files to menu
        if recent_files:
            for i, file_path in enumerate(recent_files):
                # Get the base filename for menu item
                basename = os.path.basename(file_path)
                item = self.recent_files_menu.Append(wx.ID_FILE1 + i, basename)
                self.Bind(wx.EVT_MENU, lambda evt, path=file_path: self.open_recent_file(path), item)
        else:
            # If no recent files, add a disabled item
            item = self.recent_files_menu.Append(wx.ID_ANY, "No recent files")
            item.Enable(False)
    
    def open_recent_file(self, file_path):
        """Open a file from the recent files list"""
        if os.path.exists(file_path):
            self.select_file(file_path)
            
            # Update status to show navigation hint
            if directory_image_files and len(directory_image_files) > 1:
                self.SetStatusText(f"Use ← → buttons to navigate through {len(directory_image_files)} images in folder", 0)
        else:
            # If the file no longer exists, show an error and update the menu
            self.SetStatusText(f"Error: File '{os.path.basename(file_path)}' no longer exists", 0)
            if file_path in recent_files:
                recent_files.remove(file_path)
                self.build_recent_files_menu()
    
    def update_char_count(self, event):
        """Update character count for caption abstract"""
        current_text = self.text_caption_abstract.GetValue()
        current_length = len(current_text)
        
        # Update character count label
        self.caption_char_count.SetLabel(f"{current_length}/256 characters")
        
        # Change color if over limit
        if current_length > 256:
            self.caption_char_count.SetForegroundColour(wx.Colour(255, 0, 0))  # Red
            
            # Truncate text if over limit
            self.text_caption_abstract.ChangeValue(current_text[:256])
            self.text_caption_abstract.SetInsertionPointEnd()
            
            # Update count again after truncation
            self.caption_char_count.SetLabel("256/256 characters")
        else:
            self.caption_char_count.SetForegroundColour(wx.Colour(0, 0, 0))  # Black
    
    def select_file(self, file_path=None):
        """Select a file and load its metadata"""
        global selected_file, current_file_index, directory_image_files
        
        if file_path:
            if os.path.isfile(file_path):
                selected_file = file_path
                self.selected_file = file_path
                
                # Update the filename label and path in status bar
                basename = os.path.basename(selected_file)
                self.filename_label.SetLabel(f"File: {basename}")
                self.SetStatusText(selected_file, 1)  # Show path in middle status section
                # Read metadata and update UI
                self.read_metadata()
                self.update_thumbnail()
                
                # Update preview dialog if it's open
                if self.preview_dialog and self.preview_dialog.IsShown():
                    # Create a copy of the original image to prevent any references being lost
                    if original_image and original_image.IsOk():
                        new_image = original_image.Copy()
                    else:
                        new_image = None
                        
                    self.preview_dialog.image_path = file_path
                    self.preview_dialog.original_image = new_image
                    # Force title update and image refresh
                    self.preview_dialog.SetTitle(f"Full Image: {os.path.basename(file_path)}")
                    wx.CallAfter(self.preview_dialog.update_image)  # Use CallAfter to ensure UI updates properly
                
                update_recent_files(file_path)
                self.build_recent_files_menu()
                
                # Update directory_image_files if needed
                directory = os.path.dirname(selected_file)
                if not directory_image_files or os.path.dirname(directory_image_files[0]) != directory:
                    get_directory_image_files(directory)
                
                # Find the index of the selected file in directory_image_files
                try:
                    current_file_index = directory_image_files.index(selected_file)
                except ValueError:
                    current_file_index = -1
                
                # Update navigation button states
                self.update_navigation_buttons()
            else:
                print(f"Error: The file '{file_path}' does not exist or is not accessible.")
                wx.MessageBox(f"Error: The file '{file_path}' does not exist or is not accessible.",
                              "File Error", wx.OK | wx.ICON_ERROR)
        else:
            # Open file dialog
            self.on_open()
    
    def read_metadata(self):
        """Read metadata from the selected file and populate the entry fields"""
        global selected_file
        
        if selected_file and os.path.isfile(selected_file):
            try:
                # Clear the status bar
                self.SetStatusText("Reading metadata...", 0)
                
                # Get metadata using exiftool
                # Get metadata using exiftool
                metadata = get_metadata(selected_file)
                
                # Store metadata for other methods to access
                self.metadata = metadata
                
                # Populate entry fields with metadata values
                if metadata:
                    fields_found = 0
                    
                    # Headline
                    headline = metadata.get('Headline', '')
                    self.entry_headline.SetValue(headline)
                    if headline: fields_found += 1
                    
                    # Caption/Abstract
                    caption = metadata.get('Caption-Abstract', '')
                    self.text_caption_abstract.SetValue(caption)
                    self.update_char_count(None)  # Update character count
                    if caption: fields_found += 1
                    
                    # Credit
                    credit = metadata.get('Credit', '')
                    self.entry_credit.SetValue(credit)
                    if credit: fields_found += 1
                    
                    # Object Name
                    object_name = metadata.get('Object Name', '')
                    self.entry_object_name.SetValue(object_name)
                    if object_name: fields_found += 1
                    
                    # Writer/Editor
                    writer = metadata.get('Writer-Editor', '')
                    self.entry_writer_editor.SetValue(writer)
                    if writer: fields_found += 1
                    
                    # By-line
                    byline = metadata.get('By-line', '')
                    self.entry_by_line.SetValue(byline)
                    if byline: fields_found += 1
                    
                    # Source
                    source = metadata.get('Source', '')
                    self.entry_source.SetValue(source)
                    if source: fields_found += 1
                    
                    # Date Created
                    date_created = metadata.get('Date Created', '')
                    self.entry_date.SetValue(date_created)
                    if date_created: fields_found += 1
                    
                    # Copyright Notice
                    copyright_notice = metadata.get('Copyright Notice', '')
                    self.entry_copyright_notice.SetValue(copyright_notice)
                    if copyright_notice: fields_found += 1
                    
                    # Update status bar with info about fields found
                    self.SetStatusText(f"Found {fields_found} metadata fields in {os.path.basename(selected_file)}", 0)
                else:
                    # Clear fields if no metadata
                    self.clear_fields()
                    self.SetStatusText(f"No metadata found in {os.path.basename(selected_file)}", 0)
                
                # Make sure path is still displayed (status text might have been updated)
                if selected_file:
                    self.SetStatusText(selected_file, 1)
            
            except Exception as e:
                logging.error(f"Error reading metadata: {str(e)}")
                self.SetStatusText(f"Error reading metadata: {str(e)}", 0)
                
                # Show error dialog
                wx.MessageBox(f"Error reading metadata: {str(e)}", 
                              "Metadata Error", wx.OK | wx.ICON_ERROR)
    
    def update_thumbnail(self):
        """Update the thumbnail preview with the selected image"""
        global selected_file
        
        # Clear old thumbnail if exists
        if hasattr(self, "thumbnail_bitmap"):
            del self.thumbnail_bitmap
        
        # Clear the thumbnail panel by removing its children
        for child in self.thumbnail_panel.GetChildren():
            child.Destroy()
        
        # Create new sizer for the thumbnail panel
        thumbnail_sizer = wx.BoxSizer(wx.VERTICAL)
        
        if selected_file and os.path.isfile(selected_file):
            try:
                file_ext = os.path.splitext(selected_file)[1].lower()
                is_tiff = file_ext in ['.tif', '.tiff']
                
                # For TIFF files, try to use PIL if available to avoid LibTIFF warnings
                if is_tiff and PIL_AVAILABLE:
                    try:
                        # Use PIL to load and convert the image
                        logging.debug("Loading TIFF image using PIL to avoid LibTIFF warnings")
                        pil_img = Image.open(selected_file)
                        
                        # Convert to a format wxPython can handle without warnings
                        with io.BytesIO() as temp_buffer:
                            pil_img.save(temp_buffer, format="PNG")
                            temp_buffer.seek(0)
                            
                            # Load the PNG data
                            img = wx.Image(temp_buffer, wx.BITMAP_TYPE_PNG)
                    except Exception as pil_error:
                        logging.warning(f"Failed to load image with PIL, falling back to wx.Image: {str(pil_error)}")
                        # Fall back to regular loading but suppress warnings
                        with SuppressStderr():
                            img = wx.Image(selected_file, wx.BITMAP_TYPE_ANY)
                else:
                    # For non-TIFF files or if PIL isn't available, use standard loading
                    # but suppress stderr for TIFF files to prevent warning popups
                    if is_tiff:
                        with SuppressStderr():
                            img = wx.Image(selected_file, wx.BITMAP_TYPE_ANY)
                    else:
                        img = wx.Image(selected_file, wx.BITMAP_TYPE_ANY)
                
                if img.IsOk():
                    # Save original image for potential future use
                    global original_image
                    original_image = img.Copy()
                    
                    # Scale to fit thumbnail panel (max 200x200)
                    img_width = img.GetWidth()
                    img_height = img.GetHeight()
                    
                    # Calculate scaling factor to fit within thumbnail boundaries
                    max_size = 200
                    scale_factor = min(max_size / img_width, max_size / img_height)
                    
                    # Scale image
                    new_width = int(img_width * scale_factor)
                    new_height = int(img_height * scale_factor)
                    img = img.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
                    
                    # Convert to bitmap
                    self.thumbnail_bitmap = wx.StaticBitmap(
                        self.thumbnail_panel, 
                        bitmap=wx.Bitmap(img),
                        size=(new_width, new_height)
                    )
                    
                    # Add to sizer with centering
                    thumbnail_sizer.Add(self.thumbnail_bitmap, 0, wx.ALIGN_CENTER | wx.ALL, 10)
                    
                    # Enable full image viewing
                    self.btn_view_full.Enable()
                else:
                    self.display_no_image_message(thumbnail_sizer)
            except Exception as e:
                logging.error(f"Error loading thumbnail: {str(e)}")
                self.display_no_image_message(thumbnail_sizer, error_message=str(e))
        else:
            self.display_no_image_message(thumbnail_sizer)
        
        # Set the new sizer
        self.thumbnail_panel.SetSizer(thumbnail_sizer)
        self.thumbnail_panel.Layout()
    
    def display_no_image_message(self, sizer, error_message=None):
        """Display message when no image is available"""
        message = "No image to display"
        if error_message:
            message = f"Error: {error_message}"
        
        text = wx.StaticText(self.thumbnail_panel, label=message, style=wx.ALIGN_CENTER)
        text.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(text, 1, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Disable full image viewing
        self.btn_view_full.Disable()
    
    def update_navigation_buttons(self):
        """Update navigation button states based on current file index"""
        global current_file_index, directory_image_files
        
        if current_file_index >= 0 and directory_image_files:
            # Enable prev button if not at first file
            self.nav_prev_button.Enable(current_file_index > 0)
            
            # Enable next button if not at last file
            self.nav_next_button.Enable(current_file_index < len(directory_image_files) - 1)
            
            # Update status bar with navigation info
            total_files = len(directory_image_files)
            if total_files > 1:
                self.SetStatusText(f"Image {current_file_index + 1} of {total_files}", 0)
                
                # Make sure path is still displayed
                if selected_file:
                    self.SetStatusText(selected_file, 1)
        else:
            # Disable both buttons if no valid index
            self.nav_prev_button.Disable()
            self.nav_next_button.Disable()
    
    def navigate_to_file(self, direction):
        """Navigate to next/previous file in the directory"""
        global current_file_index, directory_image_files
        
        # Calculate new index
        new_index = current_file_index + direction
        
        # Check if the new index is valid
        if 0 <= new_index < len(directory_image_files):
            next_file = directory_image_files[new_index]
            if os.path.exists(next_file):
                # Select the next file
                self.select_file(next_file)
                
                # Update status bar with navigation info
                total_files = len(directory_image_files)
                self.SetStatusText(f"Image {new_index + 1} of {total_files}", 0)
        else:
            # We've reached the end of the list
            if new_index < 0:
                self.SetStatusText("Already at first image", 0)
            else:
                self.SetStatusText("Already at last image", 0)
    
    def on_key_down(self, event):
        """Handle keyboard navigation"""
        key_code = event.GetKeyCode()
        
        # Navigate left/right with arrow keys
        if key_code == wx.WXK_LEFT:
            if self.nav_prev_button.IsEnabled():
                self.navigate_to_file(-1)
                return  # Don't skip event after handling it
        elif key_code == wx.WXK_RIGHT:
            if self.nav_next_button.IsEnabled():
                self.navigate_to_file(1)
                return  # Don't skip event after handling it
        
        # Pass event up the chain for other keys
        event.Skip()
    def clear_fields(self):
        """Clear all entry fields"""
        self.entry_headline.Clear()
        self.text_caption_abstract.Clear()
        self.entry_credit.Clear()
        self.entry_object_name.Clear()
        self.entry_writer_editor.Clear()
        self.entry_by_line.Clear()
        self.entry_source.Clear()
        self.entry_date.Clear()
        self.entry_copyright_notice.Clear()
        
        # Update character count
        # Update character count
        self.update_char_count(None)
    
    def on_clear_fields(self, event):
        """Clear all input fields when requested via menu item"""
        self.clear_fields()
        self.SetStatusText("All fields have been cleared", 0)
    
    def on_open(self, event=None):
        # Create file dialog
        wildcard = "Image files (*.jpg;*.jpeg;*.tif;*.tiff;*.png;*.gif;*.bmp)|*.jpg;*.jpeg;*.tif;*.tiff;*.png;*.gif;*.bmp|All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Choose an image file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        # Show dialog and process selection
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPath()
            self.select_file(file_path)
        
        # Clean up dialog
        dlg.Destroy()
    
    def on_write_metadata(self, event):
        """Write metadata to the selected file"""
        global selected_file
        
        if not selected_file or not os.path.isfile(selected_file):
            wx.MessageBox("No file selected. Please select an image file first.",
                         "Write Error", wx.OK | wx.ICON_WARNING)
            return
        
        try:
            # Set status
            self.SetStatusText(f"Writing metadata to {os.path.basename(selected_file)}...", 0)
            
            # Collect metadata from entry fields
            metadata = {
                'Headline': self.entry_headline.GetValue(),
                'Caption-Abstract': self.text_caption_abstract.GetValue(),
                'Credit': self.entry_credit.GetValue(),
                'ObjectName': self.entry_object_name.GetValue(),  # Note: Changed from 'Object Name' to 'ObjectName'
                'Writer-Editor': self.entry_writer_editor.GetValue(),
                'By-line': self.entry_by_line.GetValue(),
                'Source': self.entry_source.GetValue(),
                'DateCreated': self.entry_date.GetValue(),  # Note: Changed from 'Date Created' to 'DateCreated'
                'Copyright': self.entry_copyright_notice.GetValue()  # Note: Changed from 'Copyright Notice' to 'Copyright'
            }
            
            # Write metadata using exiftool
            with exiftool.ExifTool() as et:
                # Prepare command arguments
                args = []
                
                # Add each metadata field - use the correct format for ExifTool's write commands
                for tag, value in metadata.items():
                    if value:  # Only include non-empty values
                        # Format the tag correctly for writing - no spaces, just the tag name
                        args.extend([f"-{tag}={value}"])
                
                if not args:
                    wx.MessageBox("No metadata values to write. Please enter some values first.",
                                 "Write Error", wx.OK | wx.ICON_WARNING)
                    return
                
                # Add overwrite original flag
                args.append("-overwrite_original")
                
                # Add file path at the end
                args.append(selected_file)
                
                # Log the command for debugging
                logging.debug(f"ExifTool write command: {args}")
                
                # Execute command
                result = et.execute(*args)
                logging.debug(f"ExifTool write result: {result}")
                
                # Check result
                if "1 image files updated" in result:
                    self.SetStatusText(f"Metadata written to {os.path.basename(selected_file)}", 0)
                    wx.MessageBox("Metadata successfully written to file.",
                                 "Success", wx.OK | wx.ICON_INFORMATION)
                else:
                    raise Exception(f"Unexpected result: {result}")
                
        except Exception as e:
            logging.error(f"Error writing metadata: {str(e)}")
            self.SetStatusText(f"Error writing metadata: {str(e)}", 0)
            
            # Show error dialog
            wx.MessageBox(f"Error writing metadata: {str(e)}",
                         "Write Error", wx.OK | wx.ICON_ERROR)
    
    # This is a duplicate method - removing it to avoid confusion
    # The correct implementation is at line ~1206
    def on_export_data(self, event):
        """Export metadata to JSON file"""
        global selected_file
        
        if not selected_file or not os.path.isfile(selected_file):
            wx.MessageBox("No file selected. Please select an image file first.",
                         "Export Error", wx.OK | wx.ICON_WARNING)
            return
        
        # Collect metadata from entry fields
        metadata = {
            'file': os.path.basename(selected_file),
            'metadata': {
                'Headline': self.entry_headline.GetValue(),
                'Caption-Abstract': self.text_caption_abstract.GetValue(),
                'Credit': self.entry_credit.GetValue(),
                'Object Name': self.entry_object_name.GetValue(),
                'Writer-Editor': self.entry_writer_editor.GetValue(),
                'By-line': self.entry_by_line.GetValue(),
                'Source': self.entry_source.GetValue(),
                'Date Created': self.entry_date.GetValue(),
                'Copyright Notice': self.entry_copyright_notice.GetValue()
            }
        }
        
        # Create default export file name from selected file
        base_name = os.path.splitext(os.path.basename(selected_file))[0]
        default_file = f"{base_name}_metadata.json"
        
        # Create file dialog for saving
        wildcard = "JSON files (*.json)|*.json|All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message="Save metadata as JSON",
            defaultDir=os.path.dirname(selected_file),
            defaultFile=default_file,
            wildcard=wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )
        
        # Show dialog and process selection
        if dlg.ShowModal() == wx.ID_OK:
            export_path = dlg.GetPath()
            
            try:
                # Export to JSON file
                with open(export_path, 'w') as f:
                    json.dump(metadata, f, indent=4)
                
                self.SetStatusText(f"Metadata exported to {export_path}", 0)
                wx.MessageBox(f"Metadata successfully exported to {os.path.basename(export_path)}",
                             "Export Successful", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                logging.error(f"Error exporting metadata: {str(e)}")
                self.SetStatusText(f"Error exporting metadata: {str(e)}", 0)
                
                # Show error dialog
                wx.MessageBox(f"Error exporting metadata: {str(e)}",
                             "Export Error", wx.OK | wx.ICON_ERROR)
        
        dlg.Destroy()
    
    def on_view_full_image(self, event):
        """Open a dialog to view the full-sized image"""
        global selected_file, original_image
        
        if selected_file and os.path.isfile(selected_file) and original_image:
            try:
                # Check if we already have a preview dialog open
                if self.preview_dialog is not None and self.preview_dialog:
                    # If it exists but is hidden, show it
                    if not self.preview_dialog.IsShown():
                        self.preview_dialog.Show()
                    # Bring it to the foreground
                    self.preview_dialog.Raise()
                    # Update the image if it changed
                    if self.preview_dialog.image_path != selected_file:
                        self.preview_dialog.image_path = selected_file
                        self.preview_dialog.original_image = original_image
                        self.preview_dialog.update_image()
                else:
                    # Create a new dialog and show it non-modally
                    self.preview_dialog = FullImageDialog(self, selected_file, original_image)
                    self.preview_dialog.Show()
            except Exception as e:
                logging.error(f"Error displaying full image: {str(e)}")
                wx.MessageBox(f"Error displaying full image: {str(e)}",
                             "Display Error", wx.OK | wx.ICON_ERROR)
    
    def on_about(self, event):
        """Display about dialog"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Metadata Tag Writer WX")
        info.SetVersion("0.04d")
        info.SetDescription("A tool for editing IPTC metadata in image files")
        info.SetCopyright("(C) 2023-2025")
        info.SetWebSite("https://github.com/juren53/tag-writer")
        info.AddDeveloper("Jim U'Ren")
        
        wx.adv.AboutBox(info)
    
    def on_license(self, event):
        """Display license information"""
        license_text = """
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        # Create and show a dialog with the license text
        dlg = wx.Dialog(self, title="License Information", size=(600, 400))
        
        # Add a text control with the license
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.TextCtrl(dlg, style=wx.TE_MULTILINE | wx.TE_READONLY, value=license_text)
        sizer.Add(text, 1, wx.EXPAND | wx.ALL, 10)
        
        # Add a close button
        btn = wx.Button(dlg, wx.ID_CLOSE)
        btn.Bind(wx.EVT_BUTTON, lambda evt: dlg.EndModal(wx.ID_CLOSE))
        sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        dlg.SetSizer(sizer)
        dlg.ShowModal()
        dlg.Destroy()
    
    def on_usage_guide(self, event):
        """Open usage guide in web browser"""
        guide_url = "https://github.com/juren53/tag-writer/blob/main/Docs/tag-writer-help.md"

        # https://github.com/juren53/tag-writer/blob/main/Docs/tag-writer-help.md
        
        try:
            webbrowser.open(guide_url)
            self.SetStatusText(f"Opening usage guide: {guide_url}", 0)
        except Exception as e:
            logging.error(f"Error opening usage guide: {str(e)}")
            wx.MessageBox(f"Error opening usage guide: {str(e)}",
                         "Browser Error", wx.OK | wx.ICON_ERROR)
    def on_close(self, event):
        """Handle window close event"""
        # Save recent files to config
        save_recent_files()
        
        # Clean up preview dialog if it exists
        if self.preview_dialog is not None:
            self.preview_dialog.Destroy()
            self.preview_dialog = None
        
        # Continue with close
        # Continue with close
        self.Destroy()
    
    def on_exit(self, event):
        """Exit the application"""
        self.Close()
class FullImageDialog(wx.Dialog):
    """Dialog for displaying full-sized images with zoom functionality"""
    def __init__(self, parent, image_path, original_image):
        """Initialize the dialog"""
        wx.Dialog.__init__(self, parent, title="", 
                          size=(800, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.image_path = image_path
        self.original_image = original_image
        self.current_zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 0.1
        
        # Create UI components
        self.create_ui()
        
        # Bind events
        self.Bind(wx.EVT_SIZE, self.on_resize)
        
        # Update title and initial display
        self.update_title()
        self.update_image()
    
    def create_ui(self):
        """Create the user interface"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Image scroll panel (with scrollbars)
        self.scroll_panel = wx.ScrolledWindow(self, style=wx.HSCROLL | wx.VSCROLL)
        self.scroll_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.scroll_panel.SetScrollRate(10, 10)
        
        # Image display
        self.image_panel = wx.Panel(self.scroll_panel)
        self.image_bitmap = wx.StaticBitmap(self.image_panel)
        
        # Sizer for image panel
        image_sizer = wx.BoxSizer(wx.VERTICAL)
        image_sizer.Add(self.image_bitmap, 0, wx.ALL, 5)
        self.image_panel.SetSizer(image_sizer)
        
        # Sizer for scroll panel
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(self.image_panel, 1, wx.EXPAND)
        self.scroll_panel.SetSizer(scroll_sizer)
        
        # Add checkbox to control LibTIFF warnings (only if using TIFF files)
        global SUPPRESS_LIBTIFF_WARNINGS
        self.warnings_checkbox = wx.CheckBox(self, label="Suppress LibTIFF warnings")
        self.warnings_checkbox.SetValue(SUPPRESS_LIBTIFF_WARNINGS)
        self.warnings_checkbox.Bind(wx.EVT_CHECKBOX, self.on_toggle_warnings)
        main_sizer.Add(self.warnings_checkbox, 0, wx.ALL, 5)
        
        # Add scroll panel to main sizer
        main_sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # Controls panel
        controls_panel = wx.Panel(self)
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Zoom controls
        zoom_out_btn = wx.Button(controls_panel, label="-", size=(40, -1))
        zoom_out_btn.Bind(wx.EVT_BUTTON, lambda evt: self.zoom(-self.zoom_step))
        controls_sizer.Add(zoom_out_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.zoom_label = wx.StaticText(controls_panel, label="Zoom: 100%")
        controls_sizer.Add(self.zoom_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        zoom_in_btn = wx.Button(controls_panel, label="+", size=(40, -1))
        zoom_in_btn.Bind(wx.EVT_BUTTON, lambda evt: self.zoom(self.zoom_step))
        controls_sizer.Add(zoom_in_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Reset zoom button
        reset_btn = wx.Button(controls_panel, label="Reset Zoom")
        reset_btn.Bind(wx.EVT_BUTTON, lambda evt: self.reset_zoom())
        controls_sizer.Add(reset_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Fit to window button
        fit_btn = wx.Button(controls_panel, label="Fit to Window")
        fit_btn.Bind(wx.EVT_BUTTON, lambda evt: self.fit_to_window())
        controls_sizer.Add(fit_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Image info
        self.info_label = wx.StaticText(controls_panel, label="")
        controls_sizer.Add(self.info_label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Close button
        close_btn = wx.Button(controls_panel, wx.ID_CLOSE, "Close")
        close_btn.Bind(wx.EVT_BUTTON, lambda evt: self.Hide())
        controls_sizer.Add(close_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        controls_panel.SetSizer(controls_sizer)
        main_sizer.Add(controls_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        # Set main sizer
        self.SetSizer(main_sizer)
        
        # Bind mouse wheel for zooming
        self.scroll_panel.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
    
    def on_toggle_warnings(self, event):
        """Toggle LibTIFF warning suppression"""
        global SUPPRESS_LIBTIFF_WARNINGS
        SUPPRESS_LIBTIFF_WARNINGS = self.warnings_checkbox.GetValue()
        logging.debug(f"LibTIFF warning suppression set to: {SUPPRESS_LIBTIFF_WARNINGS}")
    
    def update_title(self):
        """Update the dialog title with the current image filename"""
        if self.image_path:
            new_title = f"Full Image: {os.path.basename(self.image_path)}"
            if self.GetTitle() != new_title:
                self.SetTitle(new_title)
    
    def update_image(self):
        """Update the displayed image with current zoom level"""
        # Update title first
        self.update_title()
        
        if self.original_image and self.original_image.IsOk():
            # Get original dimensions
            orig_width = self.original_image.GetWidth()
            orig_height = self.original_image.GetHeight()
            
            # Calculate new dimensions based on zoom
            new_width = int(orig_width * self.current_zoom)
            new_height = int(orig_height * self.current_zoom)
            
            # Scale the image
            if new_width > 0 and new_height > 0:
                scaled_image = self.original_image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
                
                # Convert to bitmap and update display
                bitmap = wx.Bitmap(scaled_image)
                self.image_bitmap.SetBitmap(bitmap)
                
                # Update image panel size
                self.image_panel.SetSize((new_width, new_height))
                self.scroll_panel.FitInside()
                
                # Update zoom and info labels
                self.zoom_label.SetLabel(f"Zoom: {int(self.current_zoom * 100)}%")
                self.info_label.SetLabel(f"Image Size: {orig_width} x {orig_height} pixels")
                
                # Update layout
                self.Layout()
    
    def zoom(self, zoom_delta):
        """Change the zoom level by the specified delta"""
        # Calculate new zoom level
        new_zoom = self.current_zoom + zoom_delta
        
        # Ensure zoom level is within bounds
        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.current_zoom = new_zoom
            self.update_image()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.current_zoom = 1.0
        self.update_image()
    
    def fit_to_window(self):
        """Scale the image to fit in the current window"""
        if self.original_image and self.original_image.IsOk():
            # Get original dimensions
            orig_width = self.original_image.GetWidth()
            orig_height = self.original_image.GetHeight()
            
            # Get available size (account for scrollbars and margins)
            client_width, client_height = self.scroll_panel.GetClientSize()
            available_width = max(10, client_width - 20)  # Account for margins
            available_height = max(10, client_height - 20)
            
            # Calculate scale factor to fit the window
            width_scale = available_width / orig_width
            height_scale = available_height / orig_height
            
            # Use the smaller scale to ensure the entire image fits
            self.current_zoom = min(width_scale, height_scale)
            
            # Update the display
            self.update_image()
    
    def on_resize(self, event):
        """Handle window resize events"""
        # Update the scroll panel layout
        self.scroll_panel.FitInside()
        event.Skip()
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel events for zooming"""
        # Get wheel rotation
        rotation = event.GetWheelRotation()
        
        # Determine zoom direction based on wheel rotation
        if rotation > 0:
            # Zoom in
            self.zoom(self.zoom_step)
        else:
            # Zoom out
            self.zoom(-self.zoom_step)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Metadata Tag Writer - A tool for entering and writing IPTC metadata tags")
    
    # Add arguments
    parser.add_argument("file_path", nargs="?", help="Path to an image file", default=None)
    parser.add_argument("-v", "--version", action="store_true", help="Display version information")
    
    # Parse arguments
    return parser.parse_args()

if __name__ == "__main__":
    # Create and start the application
    app = TagWriterApp()
    app.MainLoop()
    
    # Save recent files on exit
    save_recent_files()
