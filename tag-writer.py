#!/usr/bin/env python3
"""
Tag Writer - PyQt6 Implementation with Integrated Core Functionality

This is an implementation of the Tag Writer application using PyQt6
that integrates the core metadata handling and image processing functionality
from the existing codebase.
"""
#-----------------------------------------------------------
        # Tag Writer - IPTC Metadata Editor v0.07z
# 
# A GUI application for entering and writing IPTC metadata tags 
# to TIF and JPG images. Designed for free-form metadata tagging
# when metadata cannot be pulled from online databases.
#
# For complete version history and changelog, see CHANGELOG.md
#-----------------------------------------------------------

import os
import sys
import logging
import json
import exiftool
import subprocess
from datetime import datetime

# Windows console window hiding functionality
if sys.platform.startswith('win'):
    # Constants for hiding console windows on Windows
    CREATE_NO_WINDOW = 0x08000000
    SW_HIDE = 0
    
    # Windows API for taskbar icon
    import ctypes
    from ctypes import wintypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QFormLayout, QScrollArea, QSplitter, QMenu, QMenuBar,
    QStatusBar, QFileDialog, QMessageBox, QToolBar, QDialog, QProgressDialog,
    QDialogButtonBox, QInputDialog, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QPalette, QColor, QPixmap, QImage, QTextCursor, QIcon

# Note: This is a self-contained PyQt6 implementation
# All functionality is integrated within this file

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global configuration and state management
class Config:
    """Global configuration and state management"""
    def __init__(self):
        self.app_version = "0.07z"
        self.selected_file = None
        self.last_directory = None
        self.recent_files = []
        self.recent_directories = []
        self.directory_image_files = []
        self.current_file_index = -1
        self.dark_mode = False
        self.ui_zoom_factor = 1.0
        self.current_theme = 'Dark'
        self.window_geometry = None  # Store window position and size
        self.window_maximized = False  # Store window maximized state
        self.config_file = os.path.join(os.path.expanduser("~"), ".tag_writer_config.json")
        
        # Load configuration on startup
        self.load_config()
        
        # Always reset zoom to 100% on startup
        self.ui_zoom_factor = 1.0
    
    def add_recent_file(self, file_path):
        """Add a file to the recent files list"""
        if file_path and os.path.exists(file_path):
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:5]  # Keep only 5 recent files
            self.save_config()
    
    def add_recent_directory(self, directory_path):
        """Add a directory to the recent directories list"""
        if directory_path and os.path.exists(directory_path) and os.path.isdir(directory_path):
            if directory_path in self.recent_directories:
                self.recent_directories.remove(directory_path)
            self.recent_directories.insert(0, directory_path)
            self.recent_directories = self.recent_directories[:5]  # Keep only 5 recent directories
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config_data = {
                'recent_files': self.recent_files,
                'recent_directories': self.recent_directories,
                'last_directory': self.last_directory,
                'dark_mode': self.dark_mode,
                'ui_zoom_factor': self.ui_zoom_factor,
                'current_theme': self.current_theme,
                'selected_file': self.selected_file,
                'window_geometry': self.window_geometry,
                'window_maximized': self.window_maximized
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f)
            logger.debug(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                self.recent_files = [f for f in config_data.get('recent_files', []) if os.path.exists(f)]
                self.recent_directories = [d for d in config_data.get('recent_directories', []) if os.path.exists(d) and os.path.isdir(d)]
                self.last_directory = config_data.get('last_directory', None)
                self.dark_mode = config_data.get('dark_mode', False)
                self.ui_zoom_factor = config_data.get('ui_zoom_factor', 1.0)
                self.current_theme = config_data.get('current_theme', 'Dark')
                self.selected_file = config_data.get('selected_file', None)
                self.window_geometry = config_data.get('window_geometry', None)
                self.window_maximized = config_data.get('window_maximized', False)
                
                logger.debug(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

# Global configuration instance
config = Config()

def set_windows_taskbar_icon(window_handle=None):
    """Set the taskbar icon on Windows using Windows API."""
    if not sys.platform.startswith('win'):
        return False
    
    try:
        import ctypes
        from ctypes import wintypes
        
        # Find icon file
        icon_path = os.path.join(os.path.dirname(__file__), "ICON_tw.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(__file__), "ICON_tw.png")
            if not os.path.exists(icon_path):
                return False
        
        # Convert to absolute path
        icon_path = os.path.abspath(icon_path)
        
        # Set the application user model ID (helps Windows distinguish this app)
        app_id = "TagWriter.MetadataEditor.v07x"
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except:
            pass  # Ignore if not available
        
        # If we have a window handle, set the icon directly
        if window_handle:
            try:
                # Load icon from file
                if icon_path.endswith('.ico'):
                    # Load icon using Windows API
                    icon_handle = ctypes.windll.user32.LoadImageW(
                        None, icon_path, 1, 0, 0, 0x00000010 | 0x00008000
                    )
                    if icon_handle:
                        # Set both small and large icons
                        ctypes.windll.user32.SendMessageW(
                            window_handle, 0x0080, 0, icon_handle  # WM_SETICON, ICON_SMALL
                        )
                        ctypes.windll.user32.SendMessageW(
                            window_handle, 0x0080, 1, icon_handle  # WM_SETICON, ICON_BIG
                        )
            except Exception as e:
                logger.error(f"Error setting window icon via API: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting Windows taskbar icon: {e}")
        return False

def check_exiftool_availability():
    """Check if ExifTool is available and accessible.
    
    Returns:
        tuple: (is_available, version_info, error_message)
    """
    try:
        # Try to create an ExifTool instance and get version
        test_instance = create_exiftool_instance()
        with test_instance as et:
            # Try to get version info
            version_output = et.execute("-ver")
            version = version_output.strip() if version_output else "unknown"
            logger.info(f"ExifTool found - version: {version}")
            return True, version, None
    except FileNotFoundError:
        error_msg = "ExifTool executable not found. Please ensure ExifTool is installed and available in your system PATH."
        logger.error(error_msg)
        return False, None, error_msg
    except Exception as e:
        error_msg = f"ExifTool is installed but not accessible: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg

def show_exiftool_error_dialog(error_message):
    """Show an error dialog when ExifTool is not available."""
    from PyQt6.QtWidgets import QMessageBox
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("ExifTool Not Found")
    msg_box.setText("Tag Writer requires ExifTool to function properly.")
    msg_box.setDetailedText(f"Error: {error_message}\n\n"
                           "Please install ExifTool:\n"
                           "• Windows: Download from https://exiftool.org/ and add to PATH\n"
                           "• Linux: Install via package manager (e.g., 'sudo apt install exiftool')\n"
                           "• macOS: Install via Homebrew ('brew install exiftool')\n\n"
                           "After installation, restart Tag Writer.")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

def show_exiftool_success_status(window, version):
    """Show ExifTool success status in the status bar."""
    from PyQt6.QtCore import QTimer
    
    def delayed_status_update():
        try:
            if hasattr(window, 'statusBar'):
                logger.info(f"Showing ExifTool status in status bar: ExifTool v{version} ready")
                window.statusBar.showMessage(f"ExifTool v{version} ready", 5000)  # Show for 5 seconds
            else:
                logger.warning("Window does not have statusBar attribute")
        except Exception as e:
            logger.error(f"Error showing ExifTool status: {e}")
    
    # Delay the status message to ensure the window is fully initialized
    QTimer.singleShot(100, delayed_status_update)  # 100ms delay
    logger.info(f"ExifTool v{version} is ready to use")

def create_exiftool_instance():
    """Create an ExifTool instance with Windows console window properly hidden."""
    if sys.platform.startswith('win'):
        # For Windows, we need to create a custom ExifTool class that hides console windows
        class WindowsExifTool(exiftool.ExifTool):
            def run(self):
                """Override run method to hide console windows on Windows."""
                if self.running:
                    import warnings
                    warnings.warn("ExifTool already running; doing nothing.", UserWarning)
                    return
                
                # Build command args (simplified version of the original)
                proc_args = [self._executable]
                
                if hasattr(self, '_config_file') and self._config_file is not None:
                    proc_args.extend(["-config", self._config_file])
                
                proc_args.extend(["-stay_open", "True", "-@", "-"])
                
                if hasattr(self, '_common_args') and self._common_args:
                    proc_args.append("-common_args")
                    proc_args.extend(self._common_args)
                
                # Windows-specific startup info to hide console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = SW_HIDE
                
                try:
                    self._process = subprocess.Popen(
                        proc_args,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        startupinfo=startupinfo,
                        creationflags=CREATE_NO_WINDOW
                    )
                except Exception as e:
                    logger.error(f"Failed to create ExifTool process: {e}")
                    raise
                
                # Check if process started successfully
                if self._process.poll() is not None:
                    self._process = None
                    raise RuntimeError("exiftool did not execute successfully")
                
                self._running = True
                
                # Get version info (simplified)
                try:
                    if hasattr(self, '_parse_ver'):
                        self._ver = self._parse_ver()
                    else:
                        # Fallback if _parse_ver doesn't exist
                        self._ver = "unknown"
                except Exception:
                    # If version parsing fails, continue anyway
                    self._ver = "unknown"
        
        return WindowsExifTool()
    else:
        # For non-Windows platforms, use standard ExifTool
        return exiftool.ExifTool()

def get_image_files(directory):
    """Get a sorted list of image files in the directory"""
    if not directory or not os.path.exists(directory):
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff', '.bmp']
    image_files = []
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in image_extensions:
                    image_files.append(file_path)
        
        # Sort alphabetically
        image_files.sort(key=lambda x: os.path.basename(x).lower())
        return image_files
    except Exception as e:
        logger.error(f"Error getting image files from {directory}: {e}")
        return []

def backup_file(file_path):
    """Create a backup of the file with a unique name"""
    if not os.path.exists(file_path):
        return None
    
    backup_path = f"{file_path}_backup"
    counter = 1
    
    while os.path.exists(backup_path):
        backup_path = f"{file_path}_backup{counter}"
        counter += 1
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None

# Image processing helper functions
def load_image(image_path):
    """Load an image using PIL with error handling."""
    try:
        from PIL import Image
        image = Image.open(image_path)
        
        # Handle orientation from EXIF data
        try:
            from PIL.ExifTags import ORIENTATION
            exif = image.getexif()
            if exif and ORIENTATION in exif:
                orientation = exif[ORIENTATION]
                
                # Rotate image based on EXIF orientation
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except Exception as e:
            logger.debug(f"Could not process EXIF orientation: {e}")
        
        # Convert 16-bit images to 8-bit for display
        if image.mode in ['I;16', 'I;16B']:
            import numpy as np
            np_image = np.array(image)
            # Normalize to 8-bit range (0-255)
            ptp_value = np.ptp(np_image)  # Use np.ptp() instead of array.ptp()
            if ptp_value > 0:  # Avoid division by zero
                norm_image = ((np_image - np_image.min()) / ptp_value * 255).astype(np.uint8)
            else:
                norm_image = np.zeros_like(np_image, dtype=np.uint8)
            image = Image.fromarray(norm_image, mode='L')
        
        return image
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None

def create_thumbnail(pil_image, max_size):
    """Create a thumbnail from a PIL image."""
    if pil_image is None:
        return None
    
    try:
        from PIL import Image
        # Create a copy to avoid modifying the original
        thumbnail = pil_image.copy()
        
        # Handle 16-bit images (I;16 mode) by converting to a compatible mode
        if thumbnail.mode == 'I;16':
            # Convert 16-bit grayscale to 8-bit grayscale for thumbnail
            # This preserves the visual appearance while making it compatible
            thumbnail = thumbnail.convert('L')
        elif thumbnail.mode in ['I', 'F']:  # Handle other problematic modes
            # Convert to RGB for compatibility
            thumbnail = thumbnail.convert('RGB')
        
        # Handle different Pillow versions for resampling
        try:
            # Try newer Pillow version first
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            # Fall back to older Pillow version
            resample_filter = Image.LANCZOS
        
        thumbnail.thumbnail(max_size, resample_filter)
        return thumbnail
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None

def adjust_zoom(pil_image, zoom_factor):
    """Apply zoom factor to a PIL image."""
    if pil_image is None or zoom_factor <= 0:
        return None
    
    try:
        from PIL import Image
        import numpy as np
        original_width, original_height = pil_image.size
        new_width = int(original_width * zoom_factor)
        new_height = int(original_height * zoom_factor)
        
        if new_width <= 0 or new_height <= 0:
            return None
        
        # Handle different Pillow versions for resampling
        try:
            # Try newer Pillow version first
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            # Fall back to older Pillow version
            resample_filter = Image.LANCZOS
        
        # Use high-quality resampling
        resized = pil_image.resize((new_width, new_height), resample_filter)
        return resized
    except Exception as e:
        logger.error(f"Error adjusting zoom: {e}")
        return None

def read_metadata(file_path):
    """Read all metadata from an image file."""
    if not os.path.exists(file_path):
        return {}
    
    try:
        # Use hidden console window version for Windows
        et_instance = create_exiftool_instance()
        with et_instance as et:
            metadata_json = et.execute_json("-j", file_path)
            if metadata_json and len(metadata_json) > 0:
                return metadata_json[0]
            return {}
    except Exception as e:
        logger.error(f"Error reading metadata from {file_path}: {e}")
        return {}

class MetadataManager:
    """Manages image metadata operations using ExifTool"""
    
    def __init__(self):
        self.metadata = {}
        self.field_mappings = {
            'Headline': ['IPTC:Headline', 'XMP-photoshop:Headline', 'XMP:Headline', 'XMP:Title'],
            'Caption-Abstract': ['IPTC:Caption-Abstract', 'XMP:Description', 'EXIF:ImageDescription'],
            'Credit': ['IPTC:Credit', 'XMP:Credit', 'XMP-photoshop:Credit'],
            'ObjectName': ['IPTC:ObjectName', 'IPTC:Object Name', 'XMP:Title'],
            'Writer-Editor': ['IPTC:Writer-Editor', 'XMP:CaptionWriter', 'XMP-photoshop:CaptionWriter'],
            'By-line': ['IPTC:By-line', 'XMP:Creator', 'EXIF:Artist'],
            'By-lineTitle': ['IPTC:By-lineTitle', 'XMP:AuthorsPosition', 'XMP-photoshop:AuthorsPosition'],
            'Source': ['IPTC:Source', 'XMP:Source', 'XMP-photoshop:Source'],
            'DateCreated': ['IPTC:DateCreated', 'XMP:DateCreated', 'XMP-photoshop:DateCreated'],
            'DateModified': ['EXIF:ModifyDate', 'EXIF:FileModifyDate', 'XMP:ModifyDate', 'ICC_Profile:ProfileDateTime'],
            'CopyrightNotice': ['IPTC:CopyrightNotice', 'XMP:Rights', 'EXIF:Copyright'],
            'Contact': ['IPTC:Contact', 'XMP:Contact']
        }
    
    def load_from_file(self, file_path):
        """Load metadata from an image file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            # Use hidden console window version for Windows
            et_instance = create_exiftool_instance()
            with et_instance as et:
                # Get metadata
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in ['.tif', '.tiff']:
                    metadata_json = et.execute_json("-j", "-m", "-ignoreMinorErrors", file_path)
                else:
                    metadata_json = et.execute_json("-j", file_path)
                
                if metadata_json and len(metadata_json) > 0:
                    raw_metadata = metadata_json[0]
                    self.metadata = self._process_metadata(raw_metadata)
                    return True
                else:
                    self.metadata = {}
                    return False
        
        except Exception as e:
            logger.error(f"Error loading metadata from {file_path}: {e}")
            self.metadata = {}
            return False
    
    def _process_metadata(self, raw_metadata):
        """Process raw metadata to standardize field names"""
        processed = {}
        
        # Map standardized field names to raw metadata
        for field, possible_names in self.field_mappings.items():
            # Special handling for DateModified to log fallback behavior
            if field == 'DateModified':
                found_date = None
                used_field = None
                
                # Log all date-related fields in raw metadata
                logger.info("Raw metadata date fields:")
                for key, value in raw_metadata.items():
                    if any(date_key in key.lower() for date_key in ['date', 'time']):
                        logger.info(f"  {key}: {value}")
                
                # Try fields in priority order
                priority_fields = ['EXIF:ModifyDate', 'EXIF:FileModifyDate', 'XMP:ModifyDate', 'ICC_Profile:ProfileDateTime']
                
                for name in priority_fields:
                    if name in raw_metadata and raw_metadata[name]:
                        found_date = raw_metadata[name]
                        used_field = name
                        logger.info(f"Found date in {name}: {found_date}")
                        break
                
                if found_date:
                    processed[field] = found_date
                    logger.info(f"DateModified using {used_field}: {found_date}")
                else:
                    logger.info("No date found in any of the date fields")
            else:
                # Standard processing for other fields
                for name in possible_names:
                    if name in raw_metadata:
                        processed[field] = raw_metadata[name]
                        break
        
        return processed
    
    def get_field(self, field_name, default=""):
        """Get a metadata field value"""
        return self.metadata.get(field_name, default)
    
    def set_field(self, field_name, value):
        """Set a metadata field value"""
        self.metadata[field_name] = value
    
    def get_field_names(self):
        """Get all available field names"""
        return list(self.field_mappings.keys())
    
    def clear(self):
        """Clear all metadata"""
        self.metadata = {}
    
    def save_to_file(self, file_path):
        """Save metadata to an image file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            # Use hidden console window version for Windows
            et_instance = create_exiftool_instance()
            with et_instance as et:
                args = []
                
                # Add each metadata field using correct ExifTool tags
                for field_name, value in self.metadata.items():
                    if value:  # Only write non-empty values
                        # Get the primary ExifTool tag for this field
                        if field_name in self.field_mappings:
                            # Use the first (primary) tag from the mapping
                            exiftool_tag = self.field_mappings[field_name][0]
                            args.extend([f"-{exiftool_tag}={value}"])
                        else:
                            # Fallback to using field name directly (for backward compatibility)
                            args.extend([f"-{field_name}={value}"])
                
                if not args:
                    return True  # Nothing to write
                
                # Add overwrite flag and file path
                args.append("-overwrite_original")
                args.append(file_path)
                
                # Execute the command
                result = et.execute(*args)
                
                # Check if successful - look for the success message with flexible whitespace
                # and handle potential warning messages for PNG files
                success_patterns = [
                    "1 image files updated",
                    "1 image files created",
                    "files updated",
                    "files created"
                ]
                
                # Clean result string and check for success patterns
                # Handle multi-line output (warnings + success) by checking each line
                result_lines = result.strip().split('\n')
                success = False
                
                for line in result_lines:
                    line_clean = line.strip().lower()
                    if any(pattern.lower() in line_clean for pattern in success_patterns):
                        success = True
                        break
                
                # Log the ExifTool output for debugging (with sensitive info removed)
                logger.debug(f"ExifTool result: {result[:200]}...")  # Log first 200 chars
                
                return success
        
        except Exception as e:
            logger.error(f"Error saving metadata to {file_path}: {e}")
            return False
    
    def export_to_json(self, file_path):
        """Export metadata to a JSON file"""
        try:
            export_data = {
                'filename': os.path.basename(config.selected_file) if config.selected_file else 'unknown',
                'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'metadata': self.metadata
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            
            return True
        except Exception as e:
            logger.error(f"Error exporting metadata to JSON: {e}")
            return False
    
    def import_from_json(self, file_path):
        """Import metadata from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON formats
            if 'metadata' in data:
                imported_metadata = data['metadata']
            else:
                imported_metadata = data
            
            # Only import fields we recognize
            for field_name in self.get_field_names():
                if field_name in imported_metadata:
                    self.set_field(field_name, imported_metadata[field_name])
            
            return True
        except Exception as e:
            logger.error(f"Error importing metadata from JSON: {e}")
            return False


class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        self.themes = {
            'Default Light': {
                'name': 'Default Light',
                'background': '#fafafa',        # Soft off-white instead of harsh white
                'text': '#2d3748',             # Dark blue-gray instead of pure black
                'selection_bg': '#4299e1',     # Softer blue for selections
                'selection_text': '#ffffff',
                'menubar_bg': '#f7fafc',       # Very light blue-gray
                'menubar_text': '#2d3748',
                'toolbar_bg': '#f7fafc',       # Consistent with menubar
                'statusbar_bg': '#edf2f7',     # Light gray-blue
                'statusbar_text': '#4a5568',   # Medium gray
                'button_bg': '#e2e8f0',        # Light blue-gray buttons
                'button_text': '#2d3748',
                'button_hover': '#cbd5e0',     # Slightly darker on hover
                'border': '#cbd5e0'            # Soft gray borders
            },
            'Warm Light': {
                'name': 'Warm Light',
                'background': '#eee9e0',
                'text': '#504741',
                'selection_bg': '#6699cc',
                'selection_text': '#ffffff',
                'menubar_bg': '#e6e1d7',
                'menubar_text': '#504741',
                'toolbar_bg': '#f0ebe2',
                'statusbar_bg': '#e1dcd2',
                'statusbar_text': '#504741',
                'button_bg': '#e6e1d7',
                'button_text': '#504741',
                'button_hover': '#ddd8cf',
                'border': '#b4aa9a'
            },
            'Dark': {
                'name': 'Dark',
                'background': '#2b2b2b',
                'text': '#ffffff',
                'selection_bg': '#4a9eff',
                'selection_text': '#ffffff',
                'menubar_bg': '#3c3c3c',
                'menubar_text': '#ffffff',
                'toolbar_bg': '#404040',
                'statusbar_bg': '#333333',
                'statusbar_text': '#ffffff',
                'button_bg': '#454545',
                'button_text': '#ffffff',
                'button_hover': '#555555',
                'border': '#555555'
            },
            'Solarized Light': {
                'name': 'Solarized Light',
                'background': '#fdf6e3',
                'text': '#657b83',
                'selection_bg': '#268bd2',
                'selection_text': '#fdf6e3',
                'menubar_bg': '#eee8d5',
                'menubar_text': '#657b83',
                'toolbar_bg': '#f5f0e7',
                'statusbar_bg': '#eee8d5',
                'statusbar_text': '#657b83',
                'button_bg': '#eee8d5',
                'button_text': '#657b83',
                'button_hover': '#e8e2d4',
                'border': '#d3cbb7'
            },
            'Solarized Dark': {
                'name': 'Solarized Dark',
                'background': '#002b36',
                'text': '#839496',
                'selection_bg': '#268bd2',
                'selection_text': '#002b36',
                'menubar_bg': '#073642',
                'menubar_text': '#839496',
                'toolbar_bg': '#0a3c47',
                'statusbar_bg': '#073642',
                'statusbar_text': '#839496',
                'button_bg': '#073642',
                'button_text': '#839496',
                'button_hover': '#0c4956',
                'border': '#586e75'
            },
            'High Contrast': {
                'name': 'High Contrast',
                'background': '#000000',
                'text': '#ffffff',
                'selection_bg': '#ffff00',
                'selection_text': '#000000',
                'menubar_bg': '#000000',
                'menubar_text': '#ffffff',
                'toolbar_bg': '#000000',
                'statusbar_bg': '#000000',
                'statusbar_text': '#ffffff',
                'button_bg': '#333333',
                'button_text': '#ffffff',
                'button_hover': '#555555',
                'border': '#ffffff'
            },
            'Monokai': {
                'name': 'Monokai',
                'background': '#272822',
                'text': '#f8f8f2',
                'selection_bg': '#49483e',
                'selection_text': '#f8f8f2',
                'menubar_bg': '#3e3d32',
                'menubar_text': '#f8f8f2',
                'toolbar_bg': '#414339',
                'statusbar_bg': '#3e3d32',
                'statusbar_text': '#f8f8f2',
                'button_bg': '#49483e',
                'button_text': '#f8f8f2',
                'button_hover': '#5a594d',
                'border': '#75715e'
            },
            'GitHub Dark': {
                'name': 'GitHub Dark',
                'background': '#0d1117',
                'text': '#c9d1d9',
                'selection_bg': '#388bfd',
                'selection_text': '#ffffff',
                'menubar_bg': '#161b22',
                'menubar_text': '#c9d1d9',
                'toolbar_bg': '#21262d',
                'statusbar_bg': '#161b22',
                'statusbar_text': '#c9d1d9',
                'button_bg': '#21262d',
                'button_text': '#c9d1d9',
                'button_hover': '#30363d',
                'border': '#30363d'
            }
        }
        self.current_theme = 'Dark'
    
    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def get_theme(self, theme_name):
        """Get theme data by name"""
        return self.themes.get(theme_name, self.themes['Default Light'])
    
    def is_dark_theme(self, theme_name=None):
        """Check if a theme is considered dark"""
        if theme_name is None:
            theme_name = self.current_theme
        
        # Define which themes are considered dark
        dark_themes = ['Dark', 'Solarized Dark', 'High Contrast', 'Monokai']
        return theme_name in dark_themes
    
    def generate_stylesheet(self, theme_name):
        """Generate CSS stylesheet for the given theme"""
        theme = self.get_theme(theme_name)
        
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Text Edit Areas */
        QTextEdit, QPlainTextEdit {{
            background-color: {theme['background']};
            color: {theme['text']};
            selection-background-color: {theme['selection_bg']};
            selection-color: {theme['selection_text']};
            border: 1px solid {theme['border']};
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {theme['menubar_bg']};
            color: {theme['menubar_text']};
            border-bottom: 1px solid {theme['border']};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {theme['selection_bg']};
            color: {theme['selection_text']};
        }}
        
        QMenu {{
            background-color: {theme['menubar_bg']};
            color: {theme['menubar_text']};
            border: 1px solid {theme['border']};
        }}
        
        QMenu::item {{
            background-color: transparent;
            padding: 6px 12px;
        }}
        
        QMenu::item:selected {{
            background-color: {theme['selection_bg']};
            color: {theme['selection_text']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {theme['border']};
            margin: 2px 0;
        }}
        
        /* Tool Bar */
        QToolBar {{
            background-color: {theme['toolbar_bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            spacing: 2px;
        }}
        
        QToolBar::separator {{
            background-color: {theme['border']};
            width: 1px;
            margin: 2px;
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {theme['statusbar_bg']};
            color: {theme['statusbar_text']};
            border-top: 1px solid {theme['border']};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {theme['button_bg']};
            color: {theme['button_text']};
            border: 1px solid {theme['border']};
            border-radius: 3px;
            padding: 6px 12px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: {theme['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme['selection_bg']};
            color: {theme['selection_text']};
        }}
        
        QPushButton:disabled {{
            background-color: {theme['border']};
            color: {theme['statusbar_text']};
        }}
        
        /* Labels - Ensure proper text color */
        QLabel {{
            background-color: transparent;
            color: {theme['text']};
        }}
        
        /* Line Edit */
        QLineEdit {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 3px;
            padding: 4px;
            selection-background-color: {theme['selection_bg']};
            selection-color: {theme['selection_text']};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {theme['selection_bg']};
        }}
        
        /* Text Edit Focus */
        QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {theme['selection_bg']};
        }}
        
        /* Widget containers */
        QWidget {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Form layout specific styling */
        QFormLayout {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Scroll Area */
        QScrollArea {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: {theme['background']};
        }}
        
        /* Frame styling */
        QFrame {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Dialog */
        QDialog {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {theme['border']};
            width: 2px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {theme['selection_bg']};
        }}
        
        /* ComboBox */
        QComboBox {{
            background-color: {theme['button_bg']};
            color: {theme['button_text']};
            border: 1px solid {theme['border']};
            border-radius: 3px;
            padding: 4px 8px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            background-color: {theme['button_hover']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {theme['text']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {theme['menubar_bg']};
            color: {theme['menubar_text']};
            selection-background-color: {theme['selection_bg']};
            selection-color: {theme['selection_text']};
            border: 1px solid {theme['border']};
        }}
        
        /* Table Widget */
        QTableWidget {{
            background-color: {theme['background']};
            color: {theme['text']};
            selection-background-color: {theme['selection_bg']};
            selection-color: {theme['selection_text']};
            border: 1px solid {theme['border']};
        }}
        
        QTableWidget::item {{
            border-bottom: 1px solid {theme['border']};
            padding: 4px;
        }}
        
        QHeaderView::section {{
            background-color: {theme['toolbar_bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 4px;
        }}
        
        /* Scroll Bars - Enhanced visibility */
        QScrollBar:vertical {{
            background-color: {theme['background']};
            width: 16px;
            border: 1px solid {theme['border']};
            border-radius: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme['button_bg']};
            border: 1px solid {theme['selection_bg']};
            border-radius: 3px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['selection_bg']};
            border: 1px solid {theme['selection_text']};
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background-color: {theme['selection_bg']};
            border: 2px solid {theme['selection_text']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background-color: {theme['toolbar_bg']};
            border: 1px solid {theme['border']};
            height: 16px;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::add-line:vertical:hover, QScrollBar::sub-line:vertical:hover {{
            background-color: {theme['button_hover']};
        }}
        
        QScrollBar::up-arrow:vertical {{
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 6px solid {theme['text']};
        }}
        
        QScrollBar::down-arrow:vertical {{
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {theme['text']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {theme['background']};
            height: 16px;
            border: 1px solid {theme['border']};
            border-radius: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {theme['button_bg']};
            border: 1px solid {theme['selection_bg']};
            border-radius: 3px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme['selection_bg']};
            border: 1px solid {theme['selection_text']};
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background-color: {theme['selection_bg']};
            border: 2px solid {theme['selection_text']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background-color: {theme['toolbar_bg']};
            border: 1px solid {theme['border']};
            width: 16px;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::add-line:horizontal:hover, QScrollBar::sub-line:horizontal:hover {{
            background-color: {theme['button_hover']};
        }}
        
        QScrollBar::left-arrow:horizontal {{
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
            border-right: 6px solid {theme['text']};
        }}
        
        QScrollBar::right-arrow:horizontal {{
            border-top: 4px solid transparent;
            border-bottom: 4px solid transparent;
            border-left: 6px solid {theme['text']};
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}
        """


class ThemeDialog(QDialog):
    """Dialog for selecting application theme"""
    
    def __init__(self, current_theme, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.selected_theme = current_theme
        
        self.setWindowTitle("Select Theme")
        self.setFixedSize(450, 300)
        
        layout = QVBoxLayout(self)
        
        # Theme selection
        layout.addWidget(QLabel("Choose a theme for the application:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_manager.get_theme_names())
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        # Preview label
        self.preview_label = QLabel("Preview: This is how text will look with the selected theme")
        self.preview_label.setStyleSheet("padding: 15px; border: 1px solid gray; min-height: 60px;")
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label)
        
        # Preview button
        self.preview_button = QPushButton("Sample Button")
        layout.addWidget(self.preview_button)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set initial preview
        self.update_preview()
    
    def on_theme_changed(self, theme_name):
        """Handle theme selection change"""
        self.selected_theme = theme_name
        self.update_preview()
    
    def update_preview(self):
        """Update the preview with selected theme colors"""
        theme = self.theme_manager.get_theme(self.selected_theme)
        
        # Apply theme to preview elements
        self.preview_label.setStyleSheet(f"""
            background-color: {theme['background']};
            color: {theme['text']};
            padding: 15px;
            border: 1px solid {theme['border']};
            min-height: 60px;
        """)
        
        self.preview_button.setStyleSheet(f"""
            background-color: {theme['button_bg']};
            color: {theme['button_text']};
            border: 1px solid {theme['border']};
            border-radius: 3px;
            padding: 6px 12px;
        """)
    
    def get_selected_theme(self):
        """Get the selected theme name"""
        return self.selected_theme


# Legacy theme definitions for backward compatibility
LIGHT_THEME = {
    'window': QColor(238, 234, 224),       # #EEE9E0 - Soft cream background
    'text': QColor(80, 71, 65),            # #504741 - Soft dark brown text
    'button': QColor(230, 225, 215),       # #E6E1D7 - Warm, subtle beige
    'input': QColor(245, 242, 234),        # #F5F2EA - Warm cream
    'panel': QColor(225, 220, 210)         # #E1DCD2 - Gentle tan
}

DARK_THEME = {
    'window': QColor(51, 51, 51),          # #333333 - Dark gray background
    'text': QColor(240, 240, 240),         # #F0F0F0 - Light gray text
    'button': QColor(85, 85, 85),          # #555555 - Medium gray accent
    'input': QColor(68, 68, 68),           # #444444 - Slightly lighter input
    'panel': QColor(60, 60, 60)            # #3C3C3C - Slightly lighter panels
}

# Add helper function to adapt PIL image to PyQt6
def pil_to_pixmap(pil_image):
    """Convert PIL Image to QPixmap."""
    if pil_image is None:
        return None
        
    try:
        # Convert PIL Image to QImage
        from PIL import Image
        import io
        
# Handle different image modes properly
        display_image = pil_image
        
        # Convert any unsupported mode to RGB
        if pil_image.mode != 'RGB':
            display_image = pil_image.convert('RGB')
        
        # Convert to bytes
        byte_array = io.BytesIO()
        display_image.save(byte_array, format='PNG')
        
        # Create QImage from bytes
        byte_array.seek(0)
        qimg = QImage.fromData(byte_array.getvalue())
        
        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(qimg)
        return pixmap
    except Exception as e:
        logger.error(f"Error converting PIL image to QPixmap: {e}")
        return None

class MetadataPanel(QWidget):
    """Panel for displaying and editing image metadata."""
    def __init__(self, metadata_manager, parent=None):
        super().__init__(parent)
        self.metadata_manager = metadata_manager
        self.text_fields = []  # Track all text editing fields
        self.setup_ui()
        self.install_event_filters()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for metadata fields
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)
        
        # Create metadata fields with mapping to model fields
        self.headline = QLineEdit()
        self.text_fields.append(self.headline)  # Add to tracked text fields
        headline_label = QLabel("Headline:")
        headline_label.setToolTip("Title")
        headline_label.setToolTipDuration(10000)  # Show for 10 seconds
        headline_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        headline_label.setMouseTracking(True)
        form.addRow(headline_label, self.headline)
        
        # Caption/Abstract with character count
        caption_container = QWidget()
        caption_layout = QVBoxLayout(caption_container)
        caption_layout.setContentsMargins(0, 0, 0, 0)
        caption_layout.setSpacing(2)
        
        self.caption = QTextEdit()
        # Remove fixed height constraint to allow expansion - keep minimum height for usability
        self.caption.setMinimumHeight(80)
        # Set size policy to expand vertically
        from PyQt6.QtWidgets import QSizePolicy
        self.caption.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        caption_layout.addWidget(self.caption)
        
        # Character count label
        self.char_count_label = QLabel("0/1000 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setStyleSheet("font-size: 8pt;")
        caption_layout.addWidget(self.char_count_label)
        
        # Connect text changed signal to update character count
        self.caption.textChanged.connect(self.update_char_count)
        
        caption_label = QLabel("Caption/Abstract:")
        caption_label.setToolTip("Description")
        caption_label.setToolTipDuration(10000)  # Show for 10 seconds
        caption_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        caption_label.setMouseTracking(True)
        form.addRow(caption_label, caption_container)
        
        self.credit = QLineEdit()
        form.addRow("Credit:", self.credit)
        
        self.object_name = QLineEdit()
        object_name_label = QLabel("Object Name:")
        object_name_label.setToolTip("Unique Identifier / Accession Number")
        object_name_label.setToolTipDuration(10000)  # Show for 10 seconds
        object_name_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        object_name_label.setMouseTracking(True)
        form.addRow(object_name_label, self.object_name)
        
        self.byline = QLineEdit()
        byline_label = QLabel("By-line:")
        byline_label.setToolTip("Photographer")
        # Ensure tooltip is enabled and visible with better timing
        byline_label.setToolTipDuration(10000)  # Show for 10 seconds
        byline_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        # Set mouse tracking to improve tooltip responsiveness
        byline_label.setMouseTracking(True)
        form.addRow(byline_label, self.byline)
        
        self.byline_title = QLineEdit()
        byline_title_label = QLabel("By-line Title:")
        byline_title_label.setToolTip("Photographer's organization")
        byline_title_label.setToolTipDuration(10000)  # Show for 10 seconds
        byline_title_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        byline_title_label.setMouseTracking(True)
        form.addRow(byline_title_label, self.byline_title)
        
        # Create horizontal layout for Date Created and Source on same line
        date_source_container = QWidget()
        date_source_layout = QHBoxLayout(date_source_container)
        date_source_layout.setContentsMargins(0, 0, 0, 0)
        date_source_layout.setSpacing(10)
        
        # Date Created field with label
        date_label = QLabel("Date Created:")
        date_label.setMinimumWidth(90)
        self.date = QLineEdit()
        self.date.setMaximumWidth(120)
        date_source_layout.addWidget(date_label)
        date_source_layout.addWidget(self.date)
        
        # Source field with label
        source_label = QLabel("Source:")
        source_label.setMinimumWidth(50)
        self.source = QLineEdit()
        date_source_layout.addWidget(source_label)
        date_source_layout.addWidget(self.source)
        
        form.addRow(date_source_container)
        
        self.copyright = QLineEdit()
        form.addRow("Copyright Notice:", self.copyright)
        
        # Add horizontal line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #888888; margin: 5px 0px;")
        form.addRow(separator)
        
        self.additional_info = QLineEdit()
        form.addRow("Additional Info:", self.additional_info)
        
        # Create horizontal layout for Date Modified and Writer/Editor on same line
        date_writer_container = QWidget()
        date_writer_layout = QHBoxLayout(date_writer_container)
        date_writer_layout.setContentsMargins(0, 0, 0, 0)
        date_writer_layout.setSpacing(10)
        
        # Date Modified field with label
        date_mod_label = QLabel("Date Modified:")
        date_mod_label.setMinimumWidth(90)
        self.date_modified = QLineEdit()
        self.date_modified.setMaximumWidth(120)
        date_writer_layout.addWidget(date_mod_label)
        date_writer_layout.addWidget(self.date_modified)
        
        # Writer/Editor field with label
        writer_label = QLabel("Writer/Editor:")
        writer_label.setMinimumWidth(90)
        self.writer = QLineEdit()
        date_writer_layout.addWidget(writer_label)
        date_writer_layout.addWidget(self.writer)
        
        form.addRow(date_writer_container)
        
        # Add all text fields to the tracking list for keyboard focus handling
        self.text_fields.extend([
            self.credit, self.object_name, self.writer, 
            self.byline, self.byline_title, self.source, 
            self.date, self.copyright, self.additional_info, self.date_modified
        ])
        # Add caption to tracking list (it's a QTextEdit, not a QLineEdit)
        self.text_fields.append(self.caption)
        
        # Wrap form in a scroll area but allow it to expand to fill available space
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_widget.setLayout(form)
        scroll.setWidget(form_widget)
        
        # Add scroll area to main layout with stretch factor to fill space
        layout.addWidget(scroll, 1)  # Give it stretch factor to expand
        
        # Write metadata button at bottom
        self.write_button = QPushButton("Write Metadata")
        self.write_button.clicked.connect(self.on_write_metadata)
        layout.addWidget(self.write_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    
    def install_event_filters(self):
        """Install event filters on all text fields to properly handle keyboard focus."""
        for text_field in self.text_fields:
            text_field.installEventFilter(self)
    
    def eventFilter(self, watched, event):
        """Handle keyboard events in text fields to prevent arrow key propagation to main window."""
        if event.type() == event.Type.KeyPress and watched in self.text_fields:
            # When a text field has focus and Up/Down arrow keys are pressed, we need to
            # prevent the event from propagating to the application-level event filter
            # which would otherwise navigate between images
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                # We need to handle the event here (return True) to prevent it from
                # propagating to the application-level event filter, while still allowing
                # the default text cursor movement behavior
                event.accept()
                # Process the event normally for the text field
                watched.event(event)
                # Return True to indicate we've handled the event and prevent propagation
                return True
        
        # Pass all other events to the default handler
        return super().eventFilter(watched, event)
        
    def update_from_manager(self):
        """Update UI fields from metadata manager."""
        # Use field mappings for all fields
        field_mappings = {
            "Headline": self.headline,
            "Caption-Abstract": self.caption,
            "Credit": self.credit,
            "ObjectName": self.object_name,
            "Writer-Editor": self.writer,
            "By-line": self.byline,
            "By-lineTitle": self.byline_title,
            "Source": self.source,
            "DateCreated": self.date,
            "DateModified": self.date_modified,
            "Copyright Notice": self.copyright,
            "Contact": self.additional_info
        }
        
        # Special handling for copyright notice - check multiple field names
        copyright_value = self.metadata_manager.get_field("Copyright Notice", "")
        if not copyright_value:
            copyright_value = self.metadata_manager.get_field("CopyrightNotice", "")
        if not copyright_value:
            copyright_value = self.metadata_manager.get_field("Copyright", "")
        
        self.copyright.setText(copyright_value)
        print(f"Setting Copyright Notice field to: {copyright_value}")
        
        # Update each field (except copyright which we handle separately)
        for field_name, control in field_mappings.items():
            if field_name != "Copyright Notice":  # Skip copyright, handled above
                value = self.metadata_manager.get_field(field_name, "")
                if isinstance(control, QTextEdit):
                    control.setPlainText(str(value))
                else:
                    control.setText(str(value))
        
        logger.info("Updated UI from metadata manager")
    
    def update_manager_from_ui(self):
        """Update metadata manager from UI fields."""
        # Map UI controls to field names
        field_mappings = {
            "Headline": self.headline.text(),
            "Caption-Abstract": self.caption.toPlainText(),
            "Credit": self.credit.text(),
            "ObjectName": self.object_name.text(),
            "Writer-Editor": self.writer.text(),
            "By-line": self.byline.text(),
            "By-lineTitle": self.byline_title.text(),
            "Source": self.source.text(),
            "DateCreated": self.date.text(),
            "DateModified": self.date_modified.text(),
            "CopyrightNotice": self.copyright.text(),  # Use correct IPTC field name
            "Contact": self.additional_info.text()
        }
        
        # Update metadata manager
        for field_name, value in field_mappings.items():
            if value:  # Only set non-empty values
                self.metadata_manager.set_field(field_name, value)
        
        logger.info("Updated metadata manager from UI")
    
    def update_char_count(self):
        """Update the character count label for the caption field."""
        text = self.caption.toPlainText()
        count = len(text)
        
        # Update the label
        self.char_count_label.setText(f"{count} characters")
        
        # Apply visual feedback based on count
        if count > 1000:
            # Red for exceeding limit
            self.char_count_label.setStyleSheet("font-size: 8pt; color: red;")
            
            # Truncate text if over limit
            self.caption.blockSignals(True)  # Prevent recursive signal calls
            self.caption.setPlainText(text[:1000])
            self.caption.blockSignals(False)
            
            # Update count after truncation
            self.char_count_label.setText("1000 characters")
        elif count > 256:
            # Yellow for approaching limit
            self.char_count_label.setStyleSheet("font-size: 8pt; color: #FF9900;")  # Orange-yellow
        else:
            # Normal color
            self.char_count_label.setStyleSheet("font-size: 8pt;")
    
    def clear_fields(self):
        """Clear all metadata fields."""
        self.headline.clear()
        self.caption.clear()
        self.credit.clear()
        self.object_name.clear()
        self.writer.clear()
        self.byline.clear()
        self.byline_title.clear()
        self.source.clear()
        self.date.clear()
        self.copyright.clear()
        self.additional_info.clear()
        self.date_modified.clear()
        
        # Reset character count
        self.update_char_count()
        
    def set_today_date(self):
        """Set the date modified field to today's date."""
        today = datetime.now().strftime("%Y:%m:%d")
        self.date_modified.setText(today)
        logger.info(f"Set date modified field to today: {today}")
    
    def on_write_metadata(self):
        """Handle Write Metadata button click."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
        
        # Show a progress dialog
        progress_dialog = QMessageBox(QMessageBox.Icon.Information, "Writing Metadata",
                                     f"Writing metadata to {os.path.basename(config.selected_file)}...",
                                     QMessageBox.StandardButton.Ok, self)
        progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(False)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Update metadata manager from UI
            self.update_manager_from_ui()
            
            # Save to file
            if self.metadata_manager.save_to_file(config.selected_file):
                progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(True)
                progress_dialog.setText("Metadata saved successfully!")
                logger.info(f"Metadata saved to {config.selected_file}")
            else:
                progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(True)
                progress_dialog.setIcon(QMessageBox.Icon.Critical)
                progress_dialog.setText("Error saving metadata")
                logger.error(f"Error saving metadata to {config.selected_file}")
        except Exception as e:
            progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(True)
            progress_dialog.setIcon(QMessageBox.Icon.Critical)
            progress_dialog.setText(f"Error saving metadata: {str(e)}")
            logger.error(f"Exception saving metadata: {e}")

class ImageViewer(QWidget):
    """Widget for displaying and interacting with images."""
    
    def __init__(self, parent=None):
        """Initialize the image viewer."""
        super().__init__(parent)
        self.current_image_path = None
        self.pil_image = None
        self.original_thumbnail = None
        self.setup_ui()
    
    def _get_image_resolution(self, image_path):
        """Get image resolution from multiple sources with fallback."""
        try:
            import subprocess
            import json
            
            # Method 1: Try to get resolution from EXIF metadata using exiftool
            try:
                cmd = ["exiftool", "-j", "-XResolution", "-YResolution", "-ResolutionUnit", image_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    metadata_list = json.loads(result.stdout)
                    if metadata_list and isinstance(metadata_list, list) and len(metadata_list) > 0:
                        metadata = metadata_list[0]
                        
                        x_res = metadata.get('XResolution')
                        y_res = metadata.get('YResolution')
                        res_unit = metadata.get('ResolutionUnit', '').lower()
                        
                        if x_res and y_res:
                            # Handle different resolution unit formats
                            unit_suffix = "DPI"
                            if 'cm' in res_unit or 'centimeter' in res_unit:
                                unit_suffix = "DPC"  # Dots per centimeter
                            
                            # Convert to float and format
                            try:
                                x_val = float(x_res)
                                y_val = float(y_res)
                                
                                if x_val == y_val:
                                    return f"Resolution: {x_val:.0f} {unit_suffix}"
                                else:
                                    return f"Resolution: {x_val:.0f} x {y_val:.0f} {unit_suffix}"
                            except (ValueError, TypeError):
                                pass
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
                logger.debug(f"Exiftool resolution detection failed: {e}")
            
            # Method 2: Try PIL's DPI info as fallback
            if self.pil_image:
                dpi = getattr(self.pil_image, 'info', {}).get('dpi', None)
                if dpi and isinstance(dpi, (tuple, list)) and len(dpi) >= 2:
                    x_dpi, y_dpi = dpi[0], dpi[1]
                    if x_dpi and y_dpi and x_dpi > 0 and y_dpi > 0:
                        if x_dpi == y_dpi:
                            return f"Resolution: {x_dpi:.0f} DPI"
                        else:
                            return f"Resolution: {x_dpi:.0f} x {y_dpi:.0f} DPI"
            
            # Method 3: Try PIL's getexif() for JPEG files
            if self.pil_image and hasattr(self.pil_image, 'getexif'):
                try:
                    exif = self.pil_image.getexif()
                    if exif:
                        # EXIF tags for resolution
                        x_res = exif.get(282)  # XResolution
                        y_res = exif.get(283)  # YResolution
                        res_unit = exif.get(296, 2)  # ResolutionUnit (2=inches, 3=cm)
                        
                        if x_res and y_res:
                            unit_suffix = "DPI" if res_unit == 2 else "DPC"
                            
                            # Handle fractional values
                            if isinstance(x_res, tuple) and len(x_res) == 2:
                                x_val = x_res[0] / x_res[1] if x_res[1] != 0 else x_res[0]
                            else:
                                x_val = float(x_res)
                                
                            if isinstance(y_res, tuple) and len(y_res) == 2:
                                y_val = y_res[0] / y_res[1] if y_res[1] != 0 else y_res[0]
                            else:
                                y_val = float(y_res)
                            
                            if x_val > 0 and y_val > 0:
                                if x_val == y_val:
                                    return f"Resolution: {x_val:.0f} {unit_suffix}"
                                else:
                                    return f"Resolution: {x_val:.0f} x {y_val:.0f} {unit_suffix}"
                except Exception as e:
                    logger.debug(f"PIL EXIF resolution detection failed: {e}")
            
            # If all methods fail, return default
            return "Resolution: --"
            
        except Exception as e:
            logger.debug(f"Resolution detection error: {e}")
            return "Resolution: --"

    def extract_photometric_interpretation_bits_per_sample(self, image_path):
        """Extract photometric interpretation and bits per sample data using the existing metadata reading approach."""
        try:
            # Use the existing read_metadata function
            metadata = read_metadata(image_path)
            if not metadata:
                logger.debug(f"No metadata found for photometric interpretation/bits per sample extraction")
                return '--', '--'
            
            # Debug: Log all available metadata keys that might contain photometric interpretation
            relevant_keys = [key for key in metadata.keys() if 'photometric' in key.lower()]
            logger.info(f"Photometric related metadata keys found: {relevant_keys}")
            
            # Extract photometric interpretation information
            photometric_raw = metadata.get('EXIF:PhotometricInterpretation', '--')
            logger.info(f"Found raw photometric interpretation value: {photometric_raw}")
            
            # Convert numeric photometric interpretation values to descriptive text
            photometric_interpretation = self._convert_photometric_interpretation(photometric_raw)
            logger.debug(f"Converted photometric interpretation to: {photometric_interpretation}")
            
            # Extract bits per sample information
            bits_per_sample = '--'
            for field in ['File:BitsPerSample', 'BitsPerSample', 'EXIF:BitsPerSample', 'Bits Per Sample']:
                if field in metadata and metadata[field]:
                    bits_per_sample = str(metadata[field])
                    logger.debug(f"Found bits per sample field '{field}' with value: {bits_per_sample}")
                    break
            
            logger.debug(f"Final extraction result - Photometric Interpretation: {photometric_interpretation}, Bits per sample: {bits_per_sample}")
            return photometric_interpretation, bits_per_sample
            
        except Exception as e:
            logger.debug(f"Photometric Interpretation/bits per sample extraction error: {e}")
            return '--', '--'
    
    def _convert_photometric_interpretation(self, raw_value):
        """Convert numeric photometric interpretation values to descriptive text."""
        if raw_value == '--' or raw_value is None:
            return '--'
        
        # Mapping based on TIFF/EXIF specification
        photometric_map = {
            '0': 'WhiteIsZero',
            '1': 'BlackIsZero', 
            '2': 'RGB',
            '3': 'Palette',
            '4': 'Transparency Mask',
            '5': 'CMYK',
            '6': 'YCbCr',
            '8': 'CIELab',
            '9': 'ICCLab',
            '10': 'ITULab'
        }
        
        # Convert to string in case it's a number
        str_value = str(raw_value).strip()
        
        # Return the descriptive text if we have a mapping, otherwise return the original value
        return photometric_map.get(str_value, str_value)
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        # Image display area
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.image_label)
        
        # View full image button
        self.view_button = QPushButton("View Full Image")
        self.view_button.clicked.connect(self.on_view_full_image)
        layout.addWidget(self.view_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Information container for filename, dimensions, and file size with minimal spacing
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 5, 0, 0)  # Small top margin for spacing from button
        info_layout.setSpacing(8)  # Single-spaced appearance between labels
        
        # File name label
        self.filename_label = QLabel("File: --")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.filename_label)
        
        # Create hidden labels for data storage (not displayed but used for table data)
        self.dimensions_label = QLabel("Dimensions: --")
        self.file_size_label = QLabel("File size: --")
        self.resolution_label = QLabel("Resolution: --")
        self.pixel_count_label = QLabel("Pixel count: --")
        
        # Table of information using QLabel with HTML
        table_html = """
        <table style='width:100%; text-align:left; margin-left:20px; border-spacing:15px 5px;'>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>File size:</td>
                <td style='min-width:120px; padding-right:30px;'>{file_size}</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Dimension:</td>
                <td style='min-width:120px;'>{dimension}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Resolution:</td>
                <td style='min-width:120px; padding-right:30px;'>{resolution}</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Pixel count:</td>
                <td style='min-width:120px;'>{pixel_count}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Photometric Interpretation:</td>
                <td style='min-width:120px; padding-right:30px;'>{photometric_interpretation}</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Bits Per Sample:</td>
                <td style='min-width:120px;'>{bits_per_sample}</td>
            </tr>
        </table>
        """.format(
            dimension=self.dimensions_label.text().split(': ')[1],
            file_size=self.file_size_label.text().split(': ')[1],
            resolution=self.resolution_label.text().split(': ')[1],
            pixel_count=self.pixel_count_label.text().split(': ')[1],
            photometric_interpretation='--',
            bits_per_sample='--'
        )
        self.table_label = QLabel(table_html)
        info_layout.addWidget(self.table_label)

        # Add the container to the main layout
        layout.addWidget(info_container)
        
    def load_image(self, image_path):
        """Load and display an image."""
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return False
            
        try:
            # Load the image using PIL
            self.pil_image = load_image(image_path)
            if self.pil_image is None:
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            # Create original thumbnail at a reasonable max size for caching
            self.original_thumbnail = create_thumbnail(self.pil_image, (800, 800))
            if self.original_thumbnail is None:
                logger.error(f"Failed to create thumbnail for: {image_path}")
                return False
            
            # Update the thumbnail to fit the current view size
            self.update_thumbnail()
            
            # Update filename label
            filename = os.path.basename(image_path)
            self.filename_label.setText(f"File: {filename}")
            
            # Update dimensions label
            width, height = self.pil_image.size
            self.dimensions_label.setText(f"Dimensions: {width} x {height} pixels")
            
            # Update file size label
            file_size_bytes = os.path.getsize(image_path)
            # Format file size for display
            if file_size_bytes < 1024:
                file_size_str = f"{file_size_bytes} bytes"
            elif file_size_bytes < 1024 * 1024:
                file_size_str = f"{file_size_bytes / 1024:.1f} KB"
            else:
                file_size_str = f"{file_size_bytes / (1024 * 1024):.1f} MB"
            self.file_size_label.setText(f"File size: {file_size_str}")
            
            # Update resolution label with improved detection
            try:
                # Try multiple sources for resolution information
                resolution_text = self._get_image_resolution(image_path)
                self.resolution_label.setText(resolution_text)
            except Exception as e:
                logger.debug(f"Error getting resolution: {e}")
                self.resolution_label.setText("Resolution: --")
            
            # Update pixel count label
            pixel_count = width * height
            if pixel_count >= 1_000_000:
                megapixels = pixel_count / 1_000_000
                self.pixel_count_label.setText(f"Pixel count: {megapixels:.1f} MP")
            else:
                # Format with commas for readability
                formatted_count = f"{pixel_count:,}"
                self.pixel_count_label.setText(f"Pixel count: {formatted_count} pixels")
            
# Extract photometric interpretation and bits per sample
            photometric_interpretation, bits_per_sample = self.extract_photometric_interpretation_bits_per_sample(image_path)
            
            # Update table with photometric interpretation and bits per sample
            table_html = """
            <table style='width:100%; text-align:left; margin-left:20px; border-spacing:15px 5px;'>
                <tr>
                    <td style='font-weight:bold; min-width:140px; padding-right:10px;'>File size:</td>
                    <td style='min-width:120px; padding-right:30px;'>{file_size}</td>
                    <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Dimension:</td>
                    <td style='min-width:120px;'>{dimension}</td>
                </tr>
                <tr>
                    <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Resolution:</td>
                    <td style='min-width:120px; padding-right:30px;'>{resolution}</td>
                    <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Pixel count:</td>
                    <td style='min-width:120px;'>{pixel_count}</td>
                </tr>
                <tr>
<td style='font-weight:bold; min-width:140px; padding-right:10px;'>Photometric Interpretation:</td>
                    <td style='min-width:120px; padding-right:30px;'>{photometric_interpretation}</td>
                    <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Bits Per Sample:</td>
                    <td style='min-width:120px;'>{bits_per_sample}</td>
                </tr>
            </table>
            """.format(
                dimension=self.dimensions_label.text().split(': ')[1],
                file_size=self.file_size_label.text().split(': ')[1],
                resolution=self.resolution_label.text().split(': ')[1],
                pixel_count=self.pixel_count_label.text().split(': ')[1],
                photometric_interpretation=photometric_interpretation,
                bits_per_sample=bits_per_sample
            )
            self.table_label.setText(table_html)

            
            self.current_image_path = image_path
            
            return True
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return False
            
    def update_thumbnail(self):
        """Update the thumbnail to fit the current view size."""
        if self.original_thumbnail is None:
            return
        
        try:
            # Get available size of the image_label
            available_width = self.image_label.width()
            available_height = self.image_label.height()
            
            # Ensure we have minimum dimensions to work with
            if available_width < 50 or available_height < 50:
                available_width = max(available_width, 200)
                available_height = max(available_height, 200)
            
            # Create a new thumbnail that fits the available space
            thumbnail = create_thumbnail(self.original_thumbnail, (available_width, available_height))
            if thumbnail is None:
                logger.error("Failed to resize thumbnail to fit available space")
                return
            
            # Convert to QPixmap and display
            pixmap = pil_to_pixmap(thumbnail)
            if pixmap is None:
                logger.error("Failed to convert resized thumbnail to QPixmap")
                return
                
            self.image_label.setPixmap(pixmap)
            logger.info(f"Updated thumbnail to fit available space: {available_width}x{available_height}")
            
        except Exception as e:
            logger.error(f"Error updating thumbnail: {e}")
    
    def resizeEvent(self, event):
        """Handle resize events to update the thumbnail."""
        super().resizeEvent(event)
        if self.original_thumbnail:
            # Use a small delay to avoid excessive updates during resizing
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.update_thumbnail)
    
    def clear(self):
        """Clear the image display."""
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.filename_label.setText("File: --")
        self.dimensions_label.setText("Dimensions: --")
        self.file_size_label.setText("File size: --")
        self.resolution_label.setText("Resolution: --")
        self.pixel_count_label.setText("Pixel count: --")
        
        # Clear the table as well
        table_html = """
        <table style='width:100%; text-align:left; margin-left:20px; border-spacing:15px 5px;'>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>File size:</td>
                <td style='min-width:120px; padding-right:30px;'>--</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Dimension:</td>
                <td style='min-width:120px;'>--</td>
            </tr>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Resolution:</td>
                <td style='min-width:120px; padding-right:30px;'>--</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Pixel count:</td>
                <td style='min-width:120px;'>--</td>
            </tr>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Photometric Interpretation:</td>
                <td style='min-width:120px; padding-right:30px;'>--</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Bits Per Sample:</td>
                <td style='min-width:120px;'>--</td>
            </tr>
        </table>
        """
        self.table_label.setText(table_html)
        
        self.current_image_path = None
        self.pil_image = None
        self.original_thumbnail = None
    
    def show_context_menu(self, position):
        """Show context menu for the image thumbnail."""
        if not self.current_image_path:
            return
            
        # Find the main window to access its methods
        main_window = None
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'on_open_in_default_editor'):
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window is None:
            return
            
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        view_action = menu.addAction("View Full Image")
        view_action.triggered.connect(self.on_view_full_image)
        
        edit_action = menu.addAction("Open in Default Editor (Ctrl+Shift+E)")
        edit_action.triggered.connect(main_window.on_open_in_default_editor)
        
        copy_path_action = menu.addAction("Copy Path to Clipboard")
        copy_path_action.triggered.connect(lambda: main_window.on_copy_path_to_clipboard())
        
        # Show menu at cursor position
        menu.exec(self.image_label.mapToGlobal(position))
    
    def on_view_full_image(self):
        """Handle View Full Image button click."""
        if not self.current_image_path or not self.pil_image:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return
            
        # Create and show full image viewer window
        # Pass the main window instead of just self so navigation works
        main_window = self
        while main_window.parent() is not None:
            main_window = main_window.parent()
        
        viewer = FullImageViewer(main_window, self.current_image_path, self.pil_image)
        viewer.show()

class FullImageViewer(QMainWindow):
    """Main window for viewing full-sized images with maximize/minimize controls."""
    def __init__(self, parent, image_path, pil_image):
        super().__init__(parent)
        
        # Set window flags FIRST, before any other operations
        self.setWindowFlags(Qt.WindowType.Window | 
                           Qt.WindowType.WindowMinimizeButtonHint | 
                           Qt.WindowType.WindowMaximizeButtonHint | 
                           Qt.WindowType.WindowCloseButtonHint)
        
        self.parent_window = parent  # Store reference to main window
        self.image_path = image_path
        self.pil_image = pil_image
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 0.1
        self.drag_position = None
        
        # Initialize UI
        self.setup_ui()
        self.load_image()
        self.setWindowTitle(f"Full Image: {os.path.basename(self.image_path)}")
        
        # Set focus policy to accept keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Auto-fit the image to the window on startup
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.fit_to_window)  # Delay to ensure window is fully rendered
        
        # Update navigation button states
        self.update_navigation_buttons()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Important: False for proper scroll bar behavior with zoomed images
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setScaledContents(False)  # Don't scale contents, we handle scaling manually
        
        # Enable mouse tracking for dragging/panning
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.on_mouse_press
        self.image_label.mouseMoveEvent = self.on_mouse_move
        self.image_label.mouseReleaseEvent = self.on_mouse_release
        self.image_label.wheelEvent = self.on_wheel
        
        # Install event filter for keyboard events
        self.image_label.installEventFilter(self)
        
        # Set the image label directly as the scroll area widget
        self.scroll_area.setWidget(self.image_label)
        # Add scroll area to main layout (takes most of the space)
        main_layout.addWidget(self.scroll_area, stretch=1)
        
        # Create vertical layout for controls on the right side
        controls_widget = QWidget()
        controls_widget.setFixedWidth(100)  # Fixed width for control panel
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(5)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        
        # Navigation controls
        nav_group = QWidget()
        nav_layout = QVBoxLayout(nav_group)
        nav_layout.setSpacing(2)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation buttons with bold text and clear arrow symbols
        # Navigation buttons with high-contrast symbols and consistent style
        button_style = (
            "QPushButton {"
            "    padding: 8px;"
            "    letter-spacing: 1px;"
            "    background-color: #2b2b2b;"
            "    color: #ffffff;"
            "    border: 1px solid #555555;"
            "    border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #404040;"
            "    border-color: #666666;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #202020;"
            "    border-color: #888888;"
            "}"
        )
        
        self.nav_prev_btn = QPushButton("▲  Previous")
        self.nav_prev_btn.setFixedWidth(120)
        self.nav_prev_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.nav_prev_btn.setStyleSheet(button_style)
        self.nav_prev_btn.clicked.connect(self.navigate_previous)
        nav_layout.addWidget(self.nav_prev_btn)
        
        self.nav_next_btn = QPushButton("Next  ▼")
        self.nav_next_btn.setFixedWidth(120)
        self.nav_next_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.nav_next_btn.setStyleSheet(button_style)
        self.nav_next_btn.clicked.connect(self.navigate_next)
        nav_layout.addWidget(self.nav_next_btn)
        
        controls_layout.addWidget(nav_group)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        controls_layout.addWidget(separator)
        
        # Zoom controls
        zoom_group = QWidget()
        zoom_layout = QVBoxLayout(zoom_group)
        zoom_layout.setSpacing(2)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(80)
        zoom_in_btn.clicked.connect(lambda: self.zoom(self.zoom_step))
        zoom_layout.addWidget(zoom_in_btn)
        
        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zoom_layout.addWidget(self.zoom_label)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(80)
        zoom_out_btn.clicked.connect(lambda: self.zoom(-self.zoom_step))
        zoom_layout.addWidget(zoom_out_btn)
        
        controls_layout.addWidget(zoom_group)
        
        # Reset and Fit buttons
        buttons_group = QWidget()
        buttons_layout = QVBoxLayout(buttons_group)
        buttons_layout.setSpacing(2)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        reset_zoom_btn = QPushButton("Reset")
        reset_zoom_btn.setFixedWidth(80)
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        buttons_layout.addWidget(reset_zoom_btn)
        
        fit_btn = QPushButton("Fit")
        fit_btn.setFixedWidth(80)
        fit_btn.clicked.connect(self.fit_to_window)
        buttons_layout.addWidget(fit_btn)
        
        controls_layout.addWidget(buttons_group)
        
        # Add a separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        controls_layout.addWidget(separator2)
        
        # Image info (stretch to fill space)
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        controls_layout.addWidget(self.info_label, 1)
        
        # Add a separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        controls_layout.addWidget(separator3)
        
        # Close button at the bottom
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.close)
        controls_layout.addWidget(close_btn)
        
        # Add controls widget to main layout
        main_layout.addWidget(controls_widget, stretch=0)
        
        # Status bar for additional information
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def load_image(self):
        """Load and display the image."""
        if self.pil_image is None:
            return
            
        try:
            # Get original dimensions
            width, height = self.pil_image.size
            self.info_label.setText(f"Image Size: {width} x {height} pixels")
            self.status_bar.showMessage(f"Image: {os.path.basename(self.image_path)} - {width}x{height} pixels")
            
            # Convert to pixmap and display
            self.update_display()
        except Exception as e:
            logger.error(f"Error loading full image: {e}")
            QMessageBox.warning(self, "Error", f"Error loading image: {str(e)}")
    
    def update_display(self):
        """Update the image display with the current zoom level."""
        try:
            # Apply zoom
            zoomed_image = adjust_zoom(self.pil_image, self.zoom_factor)
            if zoomed_image is None:
                return
                
            # Convert to pixmap and display
            pixmap = pil_to_pixmap(zoomed_image)
            if pixmap is None:
                return
                
            self.image_label.setPixmap(pixmap)
            
            # Update the image label size to match the pixmap size
            self.image_label.setFixedSize(pixmap.size())
            
            # Update zoom label and status bar
            zoom_percent = int(self.zoom_factor * 100)
            self.zoom_label.setText(f"Zoom: {zoom_percent}%")
            
            # Update status bar with dimensions and zoom
            width, height = self.pil_image.size
            zoomed_width = int(width * self.zoom_factor)
            zoomed_height = int(height * self.zoom_factor)
            self.status_bar.showMessage(
                f"Image: {os.path.basename(self.image_path)} - " +
                f"Original: {width}x{height} - " +
                f"Zoomed: {zoomed_width}x{zoomed_height} - " +
                f"Zoom: {zoom_percent}%"
            )
        except Exception as e:
            logger.error(f"Error updating image display: {e}")
    
    def zoom(self, delta):
        """Change zoom level by delta."""
        new_zoom = self.zoom_factor + delta
        if self.min_zoom <= new_zoom <= self.max_zoom:
            # Save scroll position relative to the image
            h_scroll_bar = self.scroll_area.horizontalScrollBar()
            v_scroll_bar = self.scroll_area.verticalScrollBar()
            
            h_ratio = h_scroll_bar.value() / max(1, h_scroll_bar.maximum())
            v_ratio = v_scroll_bar.value() / max(1, v_scroll_bar.maximum())
            
            # Apply new zoom
            self.zoom_factor = new_zoom
            self.update_display()
            
            # Restore scroll position
            h_scroll_bar.setValue(int(h_ratio * h_scroll_bar.maximum()))
            v_scroll_bar.setValue(int(v_ratio * v_scroll_bar.maximum()))
    
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.zoom_factor = 1.0
        self.update_display()
        self.center_image()
    
    def center_image(self):
        """Center the image in the scroll area."""
        h_scroll_bar = self.scroll_area.horizontalScrollBar()
        v_scroll_bar = self.scroll_area.verticalScrollBar()
        
        h_scroll_bar.setValue((h_scroll_bar.maximum() - h_scroll_bar.minimum()) // 2)
        v_scroll_bar.setValue((v_scroll_bar.maximum() - v_scroll_bar.minimum()) // 2)
    
    def fit_to_window(self):
        """Scale image to fit in the current window."""
        if self.pil_image is None:
            return
            
        # Get image and viewport dimensions
        img_width, img_height = self.pil_image.size
        
        # Get the viewport size from the scroll area
        viewport_size = self.scroll_area.viewport().size()
        viewport_width = viewport_size.width() - 20  # Account for potential scrollbars
        viewport_height = viewport_size.height() - 20
        
        # Ensure minimum viewport size
        viewport_width = max(viewport_width, 100)
        viewport_height = max(viewport_height, 100)
        
        # Calculate scale factors
        width_scale = viewport_width / img_width
        height_scale = viewport_height / img_height
        
        # Use the smaller scale to ensure the entire image fits
        self.zoom_factor = min(width_scale, height_scale)
        
        # Ensure zoom factor is within bounds
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor))
        
        # Update display and center
        self.update_display()
        self.center_image()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.zoom(self.zoom_step)
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom(-self.zoom_step)
        elif event.key() == Qt.Key.Key_0:
            self.reset_zoom()
        elif event.key() == Qt.Key.Key_F:
            self.fit_to_window()
        elif event.key() == Qt.Key.Key_Up:
            self.navigate_previous()
        elif event.key() == Qt.Key.Key_Down:
            self.navigate_next()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()  # Close window
        else:
            super().keyPressEvent(event)
    
    def on_mouse_press(self, event):
        """Handle mouse press events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def on_mouse_move(self, event):
        """Handle mouse move events for panning."""
        if self.drag_position is not None:
            # Calculate distance moved
            delta = event.position() - self.drag_position
            self.drag_position = event.position()
            
            # Scroll the view
            h_scroll_bar = self.scroll_area.horizontalScrollBar()
            v_scroll_bar = self.scroll_area.verticalScrollBar()
            
            h_scroll_bar.setValue(h_scroll_bar.value() - int(delta.x()))
            v_scroll_bar.setValue(v_scroll_bar.value() - int(delta.y()))
    
    def on_mouse_release(self, event):
        """Handle mouse release events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def on_wheel(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        if delta > 0:
            # Zoom in
            self.zoom(self.zoom_step)
        elif delta < 0:
            # Zoom out
            self.zoom(-self.zoom_step)
        
        # Prevent event from propagating to parent
        event.accept()
    
    def navigate_previous(self):
        """Navigate to the previous image in the directory."""
        # Get the main window's parent (which should be the main app window)
        main_window = None
        parent = self.parent_window
        while parent and not hasattr(parent, 'on_previous'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'on_previous'):
            main_window = parent
        
        if main_window:
            # Call the main window's previous navigation
            main_window.on_previous()
            
            # Update this window with the new image
            if hasattr(config, 'selected_file') and config.selected_file:
                self.update_image_from_path(config.selected_file)
        else:
            # Fallback: try to navigate using config directly
            self.navigate_using_config(-1)
    
    def navigate_next(self):
        """Navigate to the next image in the directory."""
        # Get the main window's parent (which should be the main app window)
        main_window = None
        parent = self.parent_window
        while parent and not hasattr(parent, 'on_next'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'on_next'):
            main_window = parent
        
        if main_window:
            # Call the main window's next navigation
            main_window.on_next()
            
            # Update this window with the new image
            if hasattr(config, 'selected_file') and config.selected_file:
                self.update_image_from_path(config.selected_file)
        else:
            # Fallback: try to navigate using config directly
            self.navigate_using_config(1)
    
    def navigate_using_config(self, direction):
        """Fallback navigation using config directly with looping."""
        if not hasattr(config, 'directory_image_files') or not config.directory_image_files:
            return
        
        if not hasattr(config, 'current_file_index') or config.current_file_index < 0:
            return
        
        new_index = config.current_file_index + direction
        
        # Handle looping
        if new_index >= len(config.directory_image_files):
            new_index = 0  # Loop to first image
        elif new_index < 0:
            new_index = len(config.directory_image_files) - 1  # Loop to last image
        
        new_file = config.directory_image_files[new_index]
        config.current_file_index = new_index
        config.selected_file = new_file
        self.update_image_from_path(new_file)
    
    def update_image_from_path(self, image_path):
        """Update the full image viewer with a new image."""
        try:
            # Load the new image using PIL
            new_pil_image = load_image(image_path)
            if new_pil_image is None:
                logger.error(f"Failed to load new image: {image_path}")
                return
            
            # Update instance variables
            self.image_path = image_path
            self.pil_image = new_pil_image
            
            # Reset zoom to fit window for new image
            self.fit_to_window()
            
            # Update window title
            self.setWindowTitle(f"Full Image: {os.path.basename(image_path)}")
            
            # Update navigation buttons
            self.update_navigation_buttons()
            
        except Exception as e:
            logger.error(f"Error updating image in full viewer: {e}")
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons based on current position."""
        if not hasattr(config, 'directory_image_files') or not config.directory_image_files:
            self.nav_prev_btn.setEnabled(False)
            self.nav_next_btn.setEnabled(False)
            return
        
        if not hasattr(config, 'current_file_index') or config.current_file_index < 0:
            self.nav_prev_btn.setEnabled(False)
            self.nav_next_btn.setEnabled(False)
            return
        
        # Always enable navigation buttons when there are images (looping is enabled)
        has_images = len(config.directory_image_files) > 0
        self.nav_prev_btn.setEnabled(has_images)
        self.nav_next_btn.setEnabled(has_images)
        
        # Update status bar with position info
        total_files = len(config.directory_image_files)
        current_pos = config.current_file_index + 1
        self.status_bar.showMessage(
            f"Image: {os.path.basename(self.image_path)} - " +
            f"Image {current_pos} of {total_files} - " +
            f"Original: {self.pil_image.size[0]}x{self.pil_image.size[1]} - " +
            f"Zoom: {int(self.zoom_factor * 100)}%"
        )
    
    def eventFilter(self, obj, event):
        """Event filter to capture events from child widgets."""
        if obj is self.image_label and event.type() == event.Type.KeyPress:
            self.keyPressEvent(event)
            return True
        return super().eventFilter(obj, event)

class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.metadata_manager = MetadataManager()
        self.theme_manager = ThemeManager()
        
        # Initialize state
        self.dark_mode = config.dark_mode
        self.ui_scale_factor = config.ui_zoom_factor
        self.current_theme = getattr(config, 'current_theme', 'Default Light')
        self.theme_manager.current_theme = self.current_theme
        
        # Track if we're closing to prevent recursive close events
        self._is_closing = False
        
        # Ensure maximize button is present in the title bar
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowMinimizeButtonHint | 
            Qt.WindowType.WindowMaximizeButtonHint | 
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Set up UI
        self.setup_ui()
        
        # Install application-level event filter for arrow keys
        QApplication.instance().installEventFilter(self)
        
        # Apply saved theme
        self.apply_comprehensive_theme()
        
        # Apply saved UI zoom factor
        self.apply_ui_zoom()
        
        # Restore window geometry from saved config
        self.restore_window_geometry()
        
        logger.info("Main window initialized")
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Tag Writer")
        self.resize(1000, 600)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "ICON_tw.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback to PNG if ICO doesn't exist
            png_icon_path = os.path.join(os.path.dirname(__file__), "ICON_tw.png")
            if os.path.exists(png_icon_path):
                self.setWindowIcon(QIcon(png_icon_path))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Left/Middle section (stretches)
        path_container = QWidget()
        path_layout = QHBoxLayout(path_container)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(5)
        
        # Path and status labels
        self.path_label = QLabel("")
        path_layout.addWidget(self.path_label)
        
        self.status_label = QLabel("Ready")
        path_layout.addWidget(self.status_label)
        
        # Add the container with stretch
        self.statusBar.addWidget(path_container, 1)
        
        # Right section - Version only
        version_label = QLabel(f"Ver {config.app_version} (2025-07-24 18:42:21)")
        self.statusBar.addPermanentWidget(version_label)
        
        # Create splitter for metadata panel and image viewer
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Metadata panel (left side)
        self.metadata_panel = MetadataPanel(self.metadata_manager)
        splitter.addWidget(self.metadata_panel)
        
        # Image viewer (right side)
        self.image_viewer = ImageViewer()
        splitter.addWidget(self.image_viewer)
        
        # Set initial splitter sizes (proportional)
        splitter.setSizes([600, 400])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set up context menu for image viewer
        self.setup_image_context_menu()
        
    def setup_image_context_menu(self):
        """Set up context menu for the image viewer."""
        # The image viewer already has its context menu set up in its own class
        pass
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        
        # Recent directories submenu
        self.recent_directories_menu = file_menu.addMenu("Recent Directories")
        self.update_recent_directories_menu()
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        clear_action = QAction("&Clear Fields", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.on_clear)
        edit_menu.addAction(clear_action)
        
        edit_menu.addSeparator()
        
        export_action = QAction("&Export to JSON...", self)
        export_action.triggered.connect(self.on_export)
        edit_menu.addAction(export_action)
        
        import_action = QAction("&Import from JSON...", self)
        import_action.triggered.connect(self.on_import)
        edit_menu.addAction(import_action)
        
        edit_menu.addSeparator()
        
        date_action = QAction("Set \u0026Today's Date", self)
        date_action.triggered.connect(self.on_set_today_date)
        edit_menu.addAction(date_action)
        
        edit_menu.addSeparator()
        
        rename_action = QAction("\u0026Rename File", self)
        rename_action.triggered.connect(self.on_rename_file)
        edit_menu.addAction(rename_action)
        
        # Copy full path to clipboard
        copy_path_action = QAction("Copy F\u0026QFN to Clipboard", self)
        copy_path_action.triggered.connect(self.on_copy_path_to_clipboard)
        copy_path_action.setToolTip("Copy the Fully Qualified File Name to the clipboard")
        edit_menu.addAction(copy_path_action)
        
        # Open in default editor
        open_editor_action = QAction("Open in \u0026Default Editor", self)
        open_editor_action.triggered.connect(self.on_open_in_default_editor)
        open_editor_action.setShortcut("Ctrl+Shift+E")
        open_editor_action.setToolTip("Open the current image in your system's default image editor")
        edit_menu.addAction(open_editor_action)
        
        # Add image rotation submenu
        edit_menu.addSeparator()
        rotate_menu = edit_menu.addMenu("Rotate Image")
        
        rotate_cw_action = QAction("Rotate &Clockwise", self)
        rotate_cw_action.triggered.connect(lambda: self.on_rotate_image(90))
        rotate_menu.addAction(rotate_cw_action)
        
        rotate_ccw_action = QAction("Rotate &Counter-clockwise", self)
        rotate_ccw_action.triggered.connect(lambda: self.on_rotate_image(-90))
        rotate_menu.addAction(rotate_ccw_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        # Refresh action
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.on_refresh)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        tags_action = QAction("\u0026View All Tags...", self)
        tags_action.setShortcut("Ctrl+T")
        tags_action.triggered.connect(self.on_view_all_tags)
        view_menu.addAction(tags_action)
        
        view_menu.addSeparator()
        
        # Theme selection
        theme_action = QAction("&Theme...", self)
        theme_action.triggered.connect(self.on_select_theme)
        view_menu.addAction(theme_action)
        
        # Dark mode toggle
        self.dark_mode_action = QAction("&Toggle Dark Mode", self)
        self.dark_mode_action.setShortcut("Ctrl+D")
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.dark_mode_action.triggered.connect(self.on_toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("\u0026Help")
        
        help_action = QAction("\u0026Help", self)
        help_action.triggered.connect(self.on_help)
        help_menu.addAction(help_action)
        
        # User Guide menu item
        user_guide_action = QAction("\u0026User Guide", self)
        user_guide_action.triggered.connect(self.on_user_guide)
        help_menu.addAction(user_guide_action)
        
        # Glossary menu item
        glossary_action = QAction("\u0026Glossary", self)
        glossary_action.triggered.connect(self.on_glossary)
        help_menu.addAction(glossary_action)
        
        # Keyboard shortcuts menu item
        shortcuts_action = QAction("\u0026Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.on_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        about_action = QAction("\u0026About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Select file button
        select_btn = QPushButton("Select File")
        select_btn.clicked.connect(self.on_open)
        toolbar.addWidget(select_btn)
        
        # Navigation buttons
        # Navigation buttons with high-contrast symbols and consistent style
        button_style = (
            "QPushButton {"
            "    padding: 8px;"
            "    letter-spacing: 1px;"
            "    background-color: #2b2b2b;"
            "    color: #ffffff;"
            "    border: 1px solid #555555;"
            "    border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #404040;"
            "    border-color: #666666;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #202020;"
            "    border-color: #888888;"
            "}"
        )
        
        prev_btn = QPushButton("◀  Previous")
        prev_btn.setFixedWidth(120)
        prev_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        prev_btn.setStyleSheet(button_style)
        prev_btn.clicked.connect(self.on_previous)
        toolbar.addWidget(prev_btn)
        
        next_btn = QPushButton("Next  ▶")
        next_btn.setFixedWidth(120)
        next_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        next_btn.setStyleSheet(button_style)
        next_btn.clicked.connect(self.on_next)
        toolbar.addWidget(next_btn)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(30)
        zoom_out_btn.clicked.connect(lambda: self.zoom_ui(-0.1))
        toolbar.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel(f"UI Zoom: {int(self.ui_scale_factor * 100)}%")
        toolbar.addWidget(self.zoom_label)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(30)
        zoom_in_btn.clicked.connect(lambda: self.zoom_ui(0.1))
        toolbar.addWidget(zoom_in_btn)
        
        reset_zoom_btn = QPushButton("Reset")
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        toolbar.addWidget(reset_zoom_btn)
        
        toolbar.addSeparator()
        
        # File label (stretches to fill space)
        self.file_label = QLabel("No file selected")
        toolbar.addWidget(self.file_label)
        
    def apply_theme(self):
        """Apply the current theme to all UI elements."""
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        
        # Create a palette for the application
        palette = QPalette()
        
        # Set colors for different UI elements
        palette.setColor(QPalette.ColorRole.Window, theme['window'])
        palette.setColor(QPalette.ColorRole.WindowText, theme['text'])
        palette.setColor(QPalette.ColorRole.Base, theme['input'])
        palette.setColor(QPalette.ColorRole.AlternateBase, theme['panel'])
        palette.setColor(QPalette.ColorRole.Text, theme['text'])
        palette.setColor(QPalette.ColorRole.Button, theme['button'])
        palette.setColor(QPalette.ColorRole.ButtonText, theme['text'])
        
        # Apply palette to the application
        QApplication.instance().setPalette(palette)
        
        # Update status bar
        theme_name = "dark" if self.dark_mode else "light"
        self.status_label.setText(f"Applied {theme_name} theme")
        logger.info(f"Applied {theme_name} theme to UI")
    
    def zoom_ui(self, zoom_delta):
        """Change the UI zoom level by the specified delta."""
        # Calculate new zoom level
        new_zoom = self.ui_scale_factor + zoom_delta
        
        # Round to avoid floating point precision issues
        new_zoom = round(new_zoom, 1)
        
        # Ensure zoom level is within bounds (50% to 150%)
        if 0.5 <= new_zoom <= 1.5:
            self.ui_scale_factor = new_zoom
            self.apply_ui_zoom()
            
            # Update zoom label
            self.zoom_label.setText(f"UI Zoom: {int(self.ui_scale_factor * 100)}%")
            
            # Update config
            config.ui_zoom_factor = self.ui_scale_factor
            config.save_config()
            
            # Update status to show zoom change
            self.status_label.setText(f"UI Zoom: {int(self.ui_scale_factor * 100)}%")
        else:
            # Show feedback when zoom limit is reached
            if new_zoom > 1.5:
                self.status_label.setText("Maximum zoom reached (150%)")
            elif new_zoom < 0.5:
                self.status_label.setText("Minimum zoom reached (50%)")
    
    def reset_zoom(self):
        """Reset UI zoom to 100%."""
        self.ui_scale_factor = 1.0
        self.apply_ui_zoom()
        self.zoom_label.setText("UI Zoom: 100%")
        config.ui_zoom_factor = 1.0
        config.save_config()
    
    def apply_ui_zoom(self):
        """Apply the current zoom factor to all UI elements."""
        # Create a scaled font
        base_font_size = 9  # Base font size in points
        scaled_font_size = base_font_size * self.ui_scale_factor
        
        # Create application font
        app_font = QApplication.instance().font()
        app_font.setPointSizeF(scaled_font_size)
        QApplication.instance().setFont(app_font)
        
        # Apply scaled fonts to all widgets recursively
        self._apply_font_to_widgets(self, scaled_font_size)
        
        # Generate CSS with scaled sizes for additional UI elements
        scaled_css = f"""
        QWidget {{
            font-size: {scaled_font_size}pt;
        }}
        QPushButton {{
            font-size: {scaled_font_size}pt;
            padding: {int(6 * self.ui_scale_factor)}px {int(12 * self.ui_scale_factor)}px;
            min-width: {int(80 * self.ui_scale_factor)}px;
        }}
        QLabel {{
            font-size: {scaled_font_size}pt;
        }}
        QLineEdit {{
            font-size: {scaled_font_size}pt;
            padding: {int(4 * self.ui_scale_factor)}px;
        }}
        QTextEdit {{
            font-size: {scaled_font_size}pt;
        }}
        QComboBox {{
            font-size: {scaled_font_size}pt;
            padding: {int(4 * self.ui_scale_factor)}px {int(8 * self.ui_scale_factor)}px;
            min-width: {int(100 * self.ui_scale_factor)}px;
        }}
        QMenuBar {{
            font-size: {scaled_font_size}pt;
            padding: {int(4 * self.ui_scale_factor)}px {int(8 * self.ui_scale_factor)}px;
        }}
        QMenu {{
            font-size: {scaled_font_size}pt;
            padding: {int(6 * self.ui_scale_factor)}px {int(12 * self.ui_scale_factor)}px;
        }}
        QStatusBar {{
            font-size: {scaled_font_size}pt;
        }}
        QToolBar {{
            spacing: {int(2 * self.ui_scale_factor)}px;
        }}
        """
        
        # Get current theme stylesheet and append our zoom CSS
        current_stylesheet = QApplication.instance().styleSheet()
        # Remove any previous zoom styling
        if '/* ZOOM_STYLES_START */' in current_stylesheet:
            current_stylesheet = current_stylesheet.split('/* ZOOM_STYLES_START */')[0]
        
        # Add zoom styles
        enhanced_stylesheet = current_stylesheet + '\n/* ZOOM_STYLES_START */\n' + scaled_css + '\n/* ZOOM_STYLES_END */'
        QApplication.instance().setStyleSheet(enhanced_stylesheet)
        
        logger.info(f"Set UI zoom to {int(self.ui_scale_factor * 100)}% with font size {scaled_font_size:.1f}pt")
    
    def _apply_font_to_widgets(self, widget, font_size):
        """Recursively apply font size to all widgets."""
        try:
            # Set font for the current widget
            font = widget.font()
            font.setPointSizeF(font_size)
            widget.setFont(font)
            
            # Apply to all child widgets
            for child in widget.findChildren(QWidget):
                if child.parent() == widget:  # Only direct children to avoid duplicate processing
                    child_font = child.font()
                    child_font.setPointSizeF(font_size)
                    child.setFont(child_font)
        except Exception as e:
            # Some widgets might not support font changes, so we continue silently
            logger.debug(f"Could not apply font to widget {type(widget)}: {e}")
    
    def update_recent_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()
        
        if not config.recent_files:
            no_recent = QAction("No recent files", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
            return
        
        for i, file_path in enumerate(config.recent_files):
            if os.path.exists(file_path):
                action = QAction(f"{i+1}: {os.path.basename(file_path)}", self)
                action.triggered.connect(lambda checked=False, path=file_path: self.load_file(path))
                self.recent_menu.addAction(action)
        
        self.recent_menu.addSeparator()
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self.on_clear_recent)
        self.recent_menu.addAction(clear_action)
    
    def update_recent_directories_menu(self):
        """Update the recent directories menu."""
        self.recent_directories_menu.clear()
        
        if not config.recent_directories:
            no_recent = QAction("No recent directories", self)
            no_recent.setEnabled(False)
            self.recent_directories_menu.addAction(no_recent)
            return
        
        for i, directory_path in enumerate(config.recent_directories):
            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                # Show full path in the menu
                action = QAction(f"{i+1}: {directory_path}", self)
                action.triggered.connect(lambda checked=False, path=directory_path: self.open_directory(path))
                self.recent_directories_menu.addAction(action)
        
        self.recent_directories_menu.addSeparator()
        clear_action = QAction("Clear Recent Directories", self)
        clear_action.triggered.connect(self.on_clear_recent_directories)
        self.recent_directories_menu.addAction(clear_action)
    
    def on_open(self):
        """Handle Open action."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Image File",
            config.last_directory or "",
            "Image Files (*.jpg *.jpeg *.tif *.tiff *.png)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def on_save(self):
        """Handle Save action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
        
        # Update metadata from UI
        self.metadata_panel.update_manager_from_ui()
        
        # Save to file
        success = self.metadata_manager.save_to_file(config.selected_file)
        
        if success:
            QMessageBox.information(self, "Success", "Metadata saved successfully.")
            self.status_label.setText("Metadata saved")
        else:
            QMessageBox.critical(self, "Error", "Failed to save metadata.")
            self.status_label.setText("Error saving metadata")
    
    def on_clear(self):
        """Handle Clear Fields action."""
        self.metadata_panel.clear_fields()
        self.metadata_manager.clear()
        self.status_label.setText("All fields cleared")
    
    def on_export(self):
        """Handle Export to JSON action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        # Show file dialog
        file_dialog = QFileDialog()
        base_name = os.path.splitext(os.path.basename(config.selected_file))[0]
        default_path = f"{base_name}_metadata.json"
        start_dir = config.last_directory or ""
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Export Metadata to JSON",
            os.path.join(start_dir, default_path),
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Update metadata from UI
            self.metadata_panel.update_manager_from_ui()
            
            # Export to JSON
            if self.metadata_manager.export_to_json(file_path):
                QMessageBox.information(self, "Export Successful", f"Metadata exported to {file_path}")
                self.status_label.setText("Metadata exported")
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to export metadata.")
                self.status_label.setText("Error exporting metadata")
    
    def on_import(self):
        """Handle Import from JSON action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        # Show file dialog
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Import Metadata from JSON",
            config.last_directory or "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Import from JSON
            if self.metadata_manager.import_from_json(file_path):
                # Update UI
                self.metadata_panel.update_from_manager()
                QMessageBox.information(self, "Import Successful", f"Metadata imported from {file_path}")
                self.status_label.setText("Metadata imported")
            else:
                QMessageBox.critical(self, "Import Failed", "Failed to import metadata.")
                self.status_label.setText("Error importing metadata")
    
    def on_set_today_date(self):
        """Handle Set Today's Date action."""
        self.metadata_panel.set_today_date()
        self.status_label.setText("Date set to today")
    
    def on_copy_path_to_clipboard(self):
        """Copy the fully qualified file name (full path) to the clipboard."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        try:
            # Get the clipboard from the application
            clipboard = QApplication.clipboard()
            # Set the text to the full path of the current file
            clipboard.setText(config.selected_file)
            # Update status bar with confirmation
            self.status_label.setText(f"Full path copied to clipboard: {config.selected_file}")
        except Exception as e:
            logger.error(f"Error copying path to clipboard: {e}")
            QMessageBox.critical(self, "Error", f"Failed to copy path to clipboard: {str(e)}")
            
    def on_open_in_default_editor(self):
        """Open the current image in the system's default image editor."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
        
        try:
            # Show a warning about potential metadata changes
            result = QMessageBox.information(
                self, 
                "Opening External Editor",
                "The image will open in your default image editor.\n\n"
                "Note: Changes made in external editors may affect metadata.\n"
                "Consider refreshing the image (F5) after saving external changes.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            
            if result != QMessageBox.StandardButton.Ok:
                return
                
            # Use platform-specific method to open the file with default application
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == "Windows":
                # Windows - use the built-in 'start' command
                os.startfile(config.selected_file)
            elif system == "Darwin":  # macOS
                # macOS - use 'open' command
                subprocess.call(["open", config.selected_file])
            else:  # Linux and other Unix-like systems
                # Linux - use 'xdg-open' command
                subprocess.call(["xdg-open", config.selected_file])
                
            self.status_label.setText(f"Opened {os.path.basename(config.selected_file)} in default editor")
            
        except Exception as e:
            logger.error(f"Error opening file in default editor: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open file in default editor: {str(e)}")
    
    def on_rename_file(self):
        """Handle Rename File action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
        
        current_filename = os.path.basename(config.selected_file)
        current_directory = os.path.dirname(config.selected_file)
        
        # Create a proper modal dialog for rename with improved focus handling
        dialog = QDialog(self)
        dialog.setWindowTitle("Rename File")
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setMinimumWidth(400)
        
        # Create dialog layout
        layout = QVBoxLayout(dialog)
        
        # Add label and text field
        layout.addWidget(QLabel("Enter new filename:"))
        
        # Create line edit with the current filename
        line_edit = QLineEdit(current_filename)
        line_edit.selectAll()  # Select the entire filename for easy editing
        layout.addWidget(line_edit)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Temporarily remove application event filter
        QApplication.instance().removeEventFilter(self)
        
        # Track if dialog is shown to ensure focus is properly set
        dialog_shown = False
        original_show_event = dialog.showEvent
        
        # Override show event to force focus after dialog is visible
        def showEvent(event):
            nonlocal dialog_shown
            # Call original show event handler
            original_show_event(event)
            # Only execute once
            if not dialog_shown:
                dialog_shown = True
                # Ensure line edit gets focus AFTER the dialog is shown
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(50, lambda: line_edit.setFocus())
                QTimer.singleShot(100, lambda: line_edit.selectAll())
        
        # Override dialog show event
        dialog.showEvent = showEvent
        
        # Override key events to prevent arrow keys propagation
        def keyPressEvent(event):
            # Handle the event locally (don't propagate to parent)
            if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
                # Let the line edit handle arrow keys for cursor navigation
                # Don't call event() directly, pass to line_edit without letting parent handle it
                if line_edit.hasFocus():
                    line_edit.keyPressEvent(event)
                else:
                    # Force focus to line edit
                    line_edit.setFocus()
                    line_edit.keyPressEvent(event)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                dialog.accept()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Escape:
                dialog.reject()
                event.accept()
                return
            
            # Default handling for other keys
            QDialog.keyPressEvent(dialog, event)
        
        # Override the dialog's key press event with our custom handler
        dialog.keyPressEvent = keyPressEvent
        
        # Install event filter on the line edit to block parent events
        def lineEditEventFilter(watched, event):
            if event.type() == event.Type.KeyPress and watched == line_edit:
                # Make sure arrow keys are handled by the line edit
                if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
                    line_edit.keyPressEvent(event)
                    return True
            return False
        
        line_edit.installEventFilter(dialog)
        dialog.eventFilter = lineEditEventFilter
        
        # Show dialog and get result
        ok = dialog.exec() == QDialog.DialogCode.Accepted
        new_filename = line_edit.text() if ok else ""
        
        # Restore the application event filter
        QApplication.instance().installEventFilter(self)
        
        if not ok or not new_filename or new_filename == current_filename:
            return
        
        # Create full path for new file
        new_file_path = os.path.join(current_directory, new_filename)
        
        # Check if file already exists
        if os.path.exists(new_file_path):
            result = QMessageBox.question(
                self, "File Exists", 
                f"A file named '{new_filename}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes:
                return
        
        try:
            # Create a backup of the original file
            backup_path = backup_file(config.selected_file)
            if not backup_path:
                raise Exception("Failed to create backup file")
            
            # Rename the file
            import shutil
            shutil.move(config.selected_file, new_file_path)
            
            # Update configuration
            config.selected_file = new_file_path
            
            # Update directory image files for navigation
            if config.directory_image_files and config.current_file_index >= 0:
                config.directory_image_files[config.current_file_index] = new_file_path
            
            # Refresh UI
            self.load_file(new_file_path)
            
            self.status_label.setText(f"Renamed to {new_filename}")
            QMessageBox.information(
                self, "File Renamed", 
                f"File successfully renamed to '{new_filename}'\nA backup was created at '{os.path.basename(backup_path)}'"
            )
            
        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to rename file: {str(e)}")
            # Try to restore from backup if rename failed
            if 'backup_path' in locals() and os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, config.selected_file)
                    self.status_label.setText("Restored from backup after rename error")
                except Exception as restore_err:
                    logger.error(f"Error restoring from backup: {restore_err}")
                    self.status_label.setText("Error during rename and restore")
    
    def on_view_all_tags(self):
        """Handle View All Tags action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        metadata = read_metadata(config.selected_file)
        
        if not metadata:
            QMessageBox.information(self, "No Metadata", "No metadata found in the selected file.")
            return
        
        # Display metadata in a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"All Tags: {os.path.basename(config.selected_file)}")
        
        # Set window flags to include minimize, maximize, and close buttons
        dialog.setWindowFlags(Qt.WindowType.Window | 
                             Qt.WindowType.WindowMinimizeButtonHint | 
                             Qt.WindowType.WindowMaximizeButtonHint | 
                             Qt.WindowType.WindowCloseButtonHint)
        
        # Set dialog to full screen
        from PyQt6.QtGui import QGuiApplication
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        dialog.setGeometry(screen_geometry)
        dialog.showMaximized()
        
        layout = QVBoxLayout(dialog)
        
        # Create search bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_label = QLabel("Search:")
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Type to search tags and values (Ctrl+F to focus)")
        
        # Create search status label
        search_status = QLabel("")
        search_status.setStyleSheet("font-size: 10pt; color: gray;")
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_edit)
        search_layout.addWidget(search_status)
        
        layout.addWidget(search_container)
        
        # Create table with metadata
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Tag", "Value"])
        
        # Make table read-only - disable editing
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Set column widths - increase Tag column width by 100%
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Tag column - resizable
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)      # Value column - stretches
        
        # Set initial column widths (Tag column gets double the default width)
        table.setColumnWidth(0, 400)  # Tag column - increased to 400px (100% wider than typical 200px)
        
        # Store original metadata for filtering
        original_metadata = list(sorted(metadata.items()))
        
        # Fill table with metadata
        def populate_table(items):
            table.setRowCount(len(items))
            for i, (key, value) in enumerate(items):
                table.setItem(i, 0, QTableWidgetItem(key))
                table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        populate_table(original_metadata)
        
        # Search function
        def search_metadata():
            search_text = search_edit.text().lower()
            if not search_text:
                # Show all items if search is empty
                populate_table(original_metadata)
                search_status.setText("")
                return
            
            # Filter metadata based on search text
            filtered_items = []
            for key, value in original_metadata:
                if (search_text in key.lower() or 
                    search_text in str(value).lower()):
                    filtered_items.append((key, value))
            
            populate_table(filtered_items)
            
            # Update search status
            if filtered_items:
                search_status.setText(f"Found {len(filtered_items)} matches")
            else:
                search_status.setText("No matches found")
        
        # Connect search functionality
        search_edit.textChanged.connect(search_metadata)
        
        layout.addWidget(table)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add clear search button
        clear_btn = QPushButton("Clear Search")
        clear_btn.clicked.connect(lambda: search_edit.clear())
        button_layout.addWidget(clear_btn)
        
        # Add spacer
        button_layout.addStretch()
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addWidget(button_container)
        
        # Custom event filter for Ctrl+F shortcut
        def event_filter(watched, event):
            if event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    search_edit.setFocus()
                    search_edit.selectAll()
                    return True
                elif event.key() == Qt.Key.Key_Escape:
                    if search_edit.hasFocus() and search_edit.text():
                        search_edit.clear()
                        return True
                    else:
                        dialog.reject()
                        return True
            return False
        
        # Install event filter on dialog and table
        dialog.installEventFilter(dialog)
        table.installEventFilter(dialog)
        dialog.eventFilter = event_filter
        
        # Set initial focus to table
        table.setFocus()
        
        dialog.exec()
    
    def on_select_theme(self):
        """Handle theme selection from menu."""
        dialog = ThemeDialog(self.current_theme, self.theme_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_theme = dialog.get_selected_theme()
            if selected_theme != self.current_theme:
                self.current_theme = selected_theme
                self.theme_manager.current_theme = selected_theme
                self.apply_comprehensive_theme()
                
                # Update dark mode checkbox based on selected theme
                is_dark = selected_theme in ['Dark', 'Solarized Dark', 'High Contrast', 'Monokai']
                self.dark_mode = is_dark
                self.dark_mode_action.setChecked(self.dark_mode)
                
                # Update config
                config.current_theme = selected_theme
                config.dark_mode = self.dark_mode
                config.save_config()
                
                self.status_label.setText(f"Theme changed to {selected_theme}")
                logger.info(f"Theme changed to {selected_theme}")
    
    def apply_comprehensive_theme(self):
        """Apply the comprehensive theme system to the application."""
        try:
            # Generate and apply stylesheet
            stylesheet = self.theme_manager.generate_stylesheet(self.current_theme)
            QApplication.instance().setStyleSheet(stylesheet)
            
            # Update status bar
            self.status_label.setText(f"Applied {self.current_theme} theme")
            logger.info(f"Applied comprehensive theme: {self.current_theme}")
            
        except Exception as e:
            logger.error(f"Error applying comprehensive theme: {e}")
            # Fall back to legacy theme system
            self.apply_theme()
    
    def on_toggle_dark_mode(self):
        """Quick toggle between light and dark themes."""
        if self.theme_manager.is_dark_theme(self.current_theme):
            # Switch to light theme
            new_theme = 'Default Light'
        else:
            # Switch to dark theme
            new_theme = 'Dark'
        
        self.current_theme = new_theme
        self.theme_manager.current_theme = new_theme
        self.dark_mode = self.theme_manager.is_dark_theme(new_theme)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.apply_comprehensive_theme()
        
        # Update config
        config.current_theme = new_theme
        config.dark_mode = self.dark_mode
        config.save_config()
    
    def eventFilter(self, obj, event):
        """Application-level event filter to intercept arrow keys before they reach widgets."""
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                self.on_previous()
                return True  # Event handled, don't pass to widget
            elif event.key() == Qt.Key.Key_Down:
                self.on_next()
                return True  # Event handled, don't pass to widget
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """Handle key press events for main window navigation."""
        if event.key() == Qt.Key.Key_Up:
            self.on_previous()
            event.accept()  # Consume the event to prevent default behavior
        elif event.key() == Qt.Key.Key_Down:
            self.on_next()
            event.accept()  # Consume the event to prevent default behavior
        elif event.key() == Qt.Key.Key_F5:
            self.on_refresh()
            event.accept()  # Consume the event to prevent default behavior
        else:
            super().keyPressEvent(event)
    
    def on_previous(self):
        """Navigate to the previous image in the directory with looping."""
        if not config.directory_image_files:
            self.status_label.setText("No images in directory")
            return
        
        if config.current_file_index <= 0:
            # Loop to the last image
            config.current_file_index = len(config.directory_image_files) - 1
            self.status_label.setText("Looped to last image")
        else:
            config.current_file_index -= 1
            self.status_label.setText("Previous image")
        
        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)
    
    def on_next(self):
        """Navigate to the next image in the directory with looping."""
        if not config.directory_image_files:
            self.status_label.setText("No images in directory")
            return
        
        if config.current_file_index >= len(config.directory_image_files) - 1:
            # Loop to the first image
            config.current_file_index = 0
            self.status_label.setText("Looped to first image")
        else:
            config.current_file_index += 1
            self.status_label.setText("Next image")
        
        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)
    
    def on_clear_recent(self):
        """Clear the recent files list."""
        config.recent_files = []
        config.save_config()
        self.update_recent_menu()
        self.status_label.setText("Recent files cleared")
    
    def on_clear_recent_directories(self):
        """Clear the recent directories list."""
        config.recent_directories = []
        config.save_config()
        self.update_recent_directories_menu()
        self.status_label.setText("Recent directories cleared")
    
    def open_directory(self, directory_path):
        """Open a directory by finding the first image file and loading it."""
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            QMessageBox.warning(self, "Directory Not Found", f"The directory {directory_path} does not exist.")
            return
        
        # Get image files in the directory
        image_files = get_image_files(directory_path)
        
        if not image_files:
            QMessageBox.information(self, "No Images", f"No image files found in directory {directory_path}")
            return
        
        # Load the first image file
        first_image = image_files[0]
        self.load_file(first_image)
        
        # Add directory to recent directories
        config.add_recent_directory(directory_path)
        
        # Update recent directories menu
        self.update_recent_directories_menu()
        
        self.status_label.setText(f"Opened directory: {os.path.basename(directory_path)}")
    
    def on_rotate_image(self, degrees):
        """Rotate the current image by the specified degrees."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
        
        # Ask for confirmation
        result = QMessageBox.question(
            self,
            "Confirm Rotation",
            f"This will rotate the image {abs(degrees)}° {'clockwise' if degrees > 0 else 'counter-clockwise'}.\n\n"
            "A backup of the original file will be created before modification.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result != QMessageBox.StandardButton.Yes:
            return
        
        # Show progress dialog
        progress_dialog = QProgressDialog(
            f"Rotating image {abs(degrees)}° {'clockwise' if degrees > 0 else 'counter-clockwise'}...",
            "Cancel", 0, 100, self
        )
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(10)
        QApplication.processEvents()
        
        try:
            # Create a backup of the original file
            backup_path = backup_file(config.selected_file)
            if not backup_path:
                raise Exception("Failed to create backup file")
            
            progress_dialog.setValue(20)
            QApplication.processEvents()
            
            # Save current metadata from the UI
            self.metadata_panel.update_manager_from_ui()
            
            # Store metadata to re-apply after rotation
            # Store current metadata to re-apply after rotation
            # Store current metadata to re-apply after rotation
            # Properly get all metadata fields using the class methods
            field_names = self.metadata_manager.get_field_names()
            metadata_dict = {}
            for field_name in field_names:
                metadata_dict[field_name] = self.metadata_manager.get_field(field_name)
            
            progress_dialog.setValue(30)
            QApplication.processEvents()
            
            # Load the image
            from PIL import Image
            image = Image.open(config.selected_file)
            
            # Rotate the image
            rotated_image = image.rotate(
                -degrees,  # PIL's rotate is counter-clockwise, so negate the degrees
                expand=True  # Expand to fit the rotated image
            )
            
            progress_dialog.setValue(60)
            QApplication.processEvents()
            
            # Save the rotated image
            rotated_image.save(config.selected_file)
            
            progress_dialog.setValue(70)
            QApplication.processEvents()
            
            # Re-apply metadata to the rotated image
            # Apply each field individually
            success = True
            for field_name, value in metadata_dict.items():
                self.metadata_manager.set_field(field_name, value)
            
            # Save metadata to the rotated image
            if not self.metadata_manager.save_to_file(config.selected_file):
                raise Exception("Failed to save metadata to rotated image")
            
            progress_dialog.setValue(90)
            QApplication.processEvents()
            
            # Reload the file to update the UI
            self.load_file(config.selected_file)
            
            progress_dialog.setValue(100)
            QApplication.processEvents()
            
            # Show success message
            QMessageBox.information(
                self,
                "Rotation Complete",
                f"Image rotated {abs(degrees)}° {'clockwise' if degrees > 0 else 'counter-clockwise'} successfully.\n"
                f"Metadata preserved and backup saved to: {os.path.basename(backup_path)}"
            )
        except Exception as e:
            progress_dialog.cancel()
            logger.error(f"Error rotating image: {e}")
            QMessageBox.critical(self, "Rotation Error", f"Error rotating image: {str(e)}")
    
    def on_about(self):
        """Show About dialog."""
        QMessageBox.about(self,
            "About Tag Writer",
            f"Tag Writer version {config.app_version}\n\n"
            "A tool for editing image metadata\n\n"
            "© 2023-2025\n\n"
            "Licensed under MIT License\n"
            "Click 'User Guide' in the Help menu for more information."
        )
    
    def on_help(self):
        """Show Help dialog."""
        QMessageBox.information(self,
            "Tag Writer Help",
            "This application allows you to edit and save metadata for image files.\n\n"
            "Usage:\n"
            "1. Open an image file using File > Open or the Select File button\n"
            "2. Edit metadata fields in the left panel\n"
            "3. Click 'Write Metadata' or use File > Save to save changes\n"
            "4. Use the navigation buttons to move between images in a directory"
        )
    
    def on_user_guide(self):
        """Show User Guide from local file or GitHub URL if not found locally."""
        user_guide_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Docs", "user-guide.md")
        
        # Try to open local file first
        if os.path.exists(user_guide_file):
            try:
                # Create a dialog to display the user guide
                dialog = QDialog(self)
                dialog.setWindowTitle("Tag Writer User Guide")
                dialog.resize(700, 600)  # Larger size for better readability
                
                # Set window flags to include minimize, maximize, and close buttons
                dialog.setWindowFlags(Qt.WindowType.Window | 
                                    Qt.WindowType.WindowMinimizeButtonHint | 
                                    Qt.WindowType.WindowMaximizeButtonHint | 
                                    Qt.WindowType.WindowCloseButtonHint)
                
                layout = QVBoxLayout(dialog)
                
                # Load markdown content
                with open(user_guide_file, 'r') as f:
                    markdown_content = f.read()
                
                # Replace relative image paths with absolute paths
                markdown_content = markdown_content.replace(
                    '![Tag Writer Main Window](images/',
                    f'![Tag Writer Main Window]({os.path.dirname(os.path.abspath(__file__))}/Docs/images/')
                
                # Display in a text edit with readable font
                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                font = QFont()
                font.setPointSize(10)
                text_edit.setFont(font)
                text_edit.setMarkdown(markdown_content)
                layout.addWidget(text_edit)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
                
                dialog.exec()
                return
            except Exception as e:
                logger.error(f"Error displaying local user guide: {e}")
                # Fall through to GitHub URL
        
        # If local file doesn't exist or failed to open, open GitHub URL
        import webbrowser
        user_guide_url = "https://github.com/juren53/tag-writer/blob/main/Docs/user-guide.md"
        
        try:
            webbrowser.open(user_guide_url)
        except Exception as e:
            logger.error(f"Error opening user guide URL: {e}")
            QMessageBox.warning(self, "Error", f"Error opening user guide: {str(e)}\n\nURL: {user_guide_url}")
            
    def on_glossary(self):
        """Show Glossary from local file or GitHub URL if not found locally."""
        glossary_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Docs", "glossary.md")
        
        # Try to open local file first
        if os.path.exists(glossary_file):
            try:
                # Create a dialog to display the glossary
                dialog = QDialog(self)
                dialog.setWindowTitle("Tag Writer Glossary")
                dialog.resize(700, 600)  # Larger size for better readability
                
                # Set window flags to include minimize, maximize, and close buttons
                dialog.setWindowFlags(Qt.WindowType.Window | 
                                    Qt.WindowType.WindowMinimizeButtonHint | 
                                    Qt.WindowType.WindowMaximizeButtonHint | 
                                    Qt.WindowType.WindowCloseButtonHint)
                
                layout = QVBoxLayout(dialog)
                
                # Load markdown content
                with open(glossary_file, 'r') as f:
                    markdown_content = f.read()
                
                # Display in a text edit with readable font
                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                font = QFont()
                font.setPointSize(10)
                text_edit.setFont(font)
                text_edit.setMarkdown(markdown_content)
                layout.addWidget(text_edit)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
                
                dialog.exec()
                return
            except Exception as e:
                logger.error(f"Error displaying local glossary: {e}")
                # Fall through to GitHub URL
        
        # If local file doesn't exist or failed to open, open GitHub URL
        import webbrowser
        glossary_url = "https://github.com/juren53/tag-writer/blob/main/Docs/glossary.md"
        
        try:
            webbrowser.open(glossary_url)
        except Exception as e:
            logger.error(f"Error opening glossary URL: {e}")
            QMessageBox.warning(self, "Error", f"Error opening glossary: {str(e)}\n\nURL: {glossary_url}")
        
    def on_keyboard_shortcuts(self):
        """Show keyboard shortcuts documentation from local file or GitHub URL if not found locally."""
        # Try possible locations in order
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "Docs", "KeyBoard-ShortCuts.md"),  # Standard location
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "usr", "bin", "docs", "KeyBoard-ShortCuts.md"),  # AppImage location
            "./usr/bin/docs/KeyBoard-ShortCuts.md"  # AppImage relative location
        ]
        
        # Find first existing file
        # For Linux, case sensitivity matters
        shortcuts_file = None
        for path in possible_paths:
            if os.path.exists(path):
                shortcuts_file = path
                break

        # Debug output
        logger.info(f"Looking for keyboard shortcuts file in paths:")
        for path in possible_paths:
            logger.info(f"  {path} - {'Exists' if os.path.exists(path) else 'Not found'}")
        
        # Try to open local file first
        if os.path.exists(shortcuts_file):
            try:
                # Create a dialog to display the shortcuts
                dialog = QDialog(self)
                dialog.setWindowTitle("Keyboard Shortcuts")
                dialog.resize(600, 500)  # Larger size for better readability
                
                # Set window flags to include minimize, maximize, and close buttons
                dialog.setWindowFlags(Qt.WindowType.Window | 
                                    Qt.WindowType.WindowMinimizeButtonHint | 
                                    Qt.WindowType.WindowMaximizeButtonHint | 
                                    Qt.WindowType.WindowCloseButtonHint)
                
                layout = QVBoxLayout(dialog)
                
                # Load markdown content
                with open(shortcuts_file, 'r') as f:
                    markdown_content = f.read()
                
                # Display in a text edit with monospace font
                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                font = QFont("Monospace")
                text_edit.setFont(font)
                text_edit.setMarkdown(markdown_content)
                layout.addWidget(text_edit)
                
                # Close button
                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
                
                dialog.exec()
                return
            except Exception as e:
                logger.error(f"Error displaying local keyboard shortcuts: {e}")
                # Fall through to GitHub URL
        
        # If local file doesn't exist or failed to open, open GitHub URL
        import webbrowser
        shortcuts_url = "https://github.com/juren53/tag-writer/blob/main/Docs/KeyBoard-ShortCuts.md"
        
        try:
            webbrowser.open(shortcuts_url)
        except Exception as e:
            logger.error(f"Error opening keyboard shortcuts URL: {e}")
            QMessageBox.warning(self, "Error", f"Error opening keyboard shortcuts: {str(e)}\n\nURL: {shortcuts_url}")
        
    def on_refresh(self):
        """Refresh the current image and metadata."""
        if not config.selected_file:
            self.status_label.setText("No file to refresh")
            return
            
        file_path = config.selected_file
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file {file_path} no longer exists.")
            self.status_label.setText("File not found")
            return
        
        # Save current cursor positions and selections in text fields
        cursor_positions = {}
        selections = {}
        field_mappings = {
            "headline": self.metadata_panel.headline,
            "caption": self.metadata_panel.caption,
            "credit": self.metadata_panel.credit,
            "object_name": self.metadata_panel.object_name,
            "writer": self.metadata_panel.writer,
            "byline": self.metadata_panel.byline,
            "byline_title": self.metadata_panel.byline_title,
            "source": self.metadata_panel.source,
            "date": self.metadata_panel.date,
            "copyright": self.metadata_panel.copyright,
            "additional_info": self.metadata_panel.additional_info,
            "date_modified": self.metadata_panel.date_modified
        }
        
        # Store cursor positions and selections for all text fields
        for field_name, widget in field_mappings.items():
            if isinstance(widget, QLineEdit):
                cursor_positions[field_name] = widget.cursorPosition()
                selections[field_name] = (widget.selectionStart(), widget.selectionLength())
            elif isinstance(widget, QTextEdit):
                cursor = widget.textCursor()
                cursor_positions[field_name] = cursor.position()
                selections[field_name] = (cursor.selectionStart(), cursor.selectionEnd())
        
        # Show temporary status
        self.status_label.setText("Refreshing...")
        QApplication.processEvents()
        
        # Reload metadata from file
        self.metadata_manager.load_from_file(file_path)
        self.metadata_panel.update_from_manager()
        
        # Reload image
        self.image_viewer.load_image(file_path)
        
        # Restore cursor positions and selections
        for field_name, widget in field_mappings.items():
            if isinstance(widget, QLineEdit) and field_name in cursor_positions:
                widget.setCursorPosition(cursor_positions[field_name])
                if selections[field_name][1] > 0:  # If there was a selection
                    widget.setSelection(selections[field_name][0], selections[field_name][1])
            elif isinstance(widget, QTextEdit) and field_name in cursor_positions:
                cursor = widget.textCursor()
                cursor.setPosition(cursor_positions[field_name])
                if selections[field_name][0] != selections[field_name][1]:  # If there was a selection
                    cursor.setPosition(selections[field_name][0])
                    cursor.setPosition(selections[field_name][1], QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor)
        
        # Update UI
        self.file_label.setText(os.path.basename(file_path))
        self.path_label.setText(os.path.dirname(file_path))
        
        # Update status
        self.status_label.setText(f"Refreshed {os.path.basename(file_path)}")
        logger.info(f"Refreshed file: {file_path}")
    
    def load_file(self, file_path):
        """Load an image file and update the UI."""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file {file_path} does not exist.")
            return False
        
        # Update configuration
        config.selected_file = file_path
        config.add_recent_file(file_path)
        
        # Get directory image files for navigation
        directory = os.path.dirname(file_path)
        config.last_directory = directory
        config.directory_image_files = get_image_files(directory)
        
        # Add directory to recent directories
        config.add_recent_directory(directory)
        
        # Update recent directories menu
        self.update_recent_directories_menu()
        
        try:
            # Find index of current file
            config.current_file_index = config.directory_image_files.index(file_path)
        except ValueError:
            config.current_file_index = -1
        
        # Load metadata
        if not self.metadata_manager.load_from_file(file_path):
            # If no metadata, just clear the fields
            self.metadata_panel.clear_fields()
        
        # Update UI from metadata
        self.metadata_panel.update_from_manager()
        
        # Load image
        if not self.image_viewer.load_image(file_path):
            QMessageBox.warning(self, "Error", f"Failed to load image: {file_path}")
            return False
        
        # Update UI
        self.file_label.setText(os.path.basename(file_path))
        self.path_label.setText(os.path.dirname(file_path))
        self.setWindowTitle(f"Tag Writer - {os.path.basename(file_path)}")
        self.status_label.setText(f"Loaded {os.path.basename(file_path)}")
        
        # Update recent files menu
        self.update_recent_menu()
        
        logger.info(f"Loaded file: {file_path}")
        return True
    
    def save_window_geometry(self):
        """Save the current window geometry and state to config."""
        try:
            # Save window geometry as a list [x, y, width, height]
            geometry = self.geometry()
            config.window_geometry = [geometry.x(), geometry.y(), geometry.width(), geometry.height()]
            
            # Save window maximized state
            config.window_maximized = self.isMaximized()
            
            # Save configuration
            config.save_config()
            
            logger.debug(f"Window geometry saved: {config.window_geometry}, maximized: {config.window_maximized}")
        except Exception as e:
            logger.error(f"Error saving window geometry: {e}")
    
    def restore_window_geometry(self):
        """Restore window geometry and state from config."""
        try:
            if config.window_geometry and len(config.window_geometry) == 4:
                x, y, width, height = config.window_geometry
                
                # Ensure the window position is on screen (basic validation)
                from PyQt6.QtGui import QGuiApplication
                screen_geometry = QGuiApplication.primaryScreen().geometry()
                
                # Clamp position to screen bounds
                x = max(0, min(x, screen_geometry.width() - width))
                y = max(0, min(y, screen_geometry.height() - height))
                
                # Ensure minimum size
                width = max(600, width)
                height = max(400, height)
                
                # Set the geometry
                self.setGeometry(x, y, width, height)
                
                # Restore maximized state if it was maximized
                if config.window_maximized:
                    self.showMaximized()
                
                logger.debug(f"Window geometry restored: {[x, y, width, height]}, maximized: {config.window_maximized}")
            else:
                logger.debug("No saved window geometry found, using default size")
        except Exception as e:
            logger.error(f"Error restoring window geometry: {e}")
            # Fall back to default size if restoration fails
            self.resize(1000, 600)
    
    def cleanup_resources(self):
        """Clean up resources before closing."""
        try:
            # Save window geometry before closing
            self.save_window_geometry()
            
            # Save current configuration
            config.save_config()
            
            # Clear event filters to prevent further processing
            if hasattr(self, 'metadata_panel'):
                QApplication.instance().removeEventFilter(self)
            
            # Clear image resources
            if hasattr(self, 'image_viewer'):
                self.image_viewer.clear()
            
            # Clear metadata
            if hasattr(self, 'metadata_manager'):
                self.metadata_manager.clear()
            
            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def closeEvent(self, event):
        """Handle close events to ensure proper shutdown."""
        # Prevent recursive close events
        if self._is_closing:
            event.accept()
            return
        
        self._is_closing = True
        
        try:
            # Cleanup resources
            self.cleanup_resources()
            
            # Accept the close event
            event.accept()
            
            # Force application quit
            QApplication.instance().quit()
            
        except Exception as e:
            logger.error(f"Error during close event: {e}")
            # Force quit even if there's an error
            event.accept()
            QApplication.instance().quit()

def main():
    """Run the application."""
    app = QApplication(sys.argv)
    
    # Set Windows taskbar icon early (before window creation)
    set_windows_taskbar_icon()
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application to quit when last window is closed
    app.setQuitOnLastWindowClosed(True)
    
    # Set application icon (affects taskbar icon)
    icon_path = os.path.join(os.path.dirname(__file__), "ICON_tw.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        # Fallback to PNG if ICO doesn't exist
        png_icon_path = os.path.join(os.path.dirname(__file__), "ICON_tw.png")
        if os.path.exists(png_icon_path):
            app.setWindowIcon(QIcon(png_icon_path))
    
    # Check ExifTool availability before proceeding
    is_available, version, error_msg = check_exiftool_availability()
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Set taskbar icon with window handle after window is shown
    if sys.platform.startswith('win'):
        try:
            # Get the window handle
            window_handle = int(window.winId())
            set_windows_taskbar_icon(window_handle)
        except Exception as e:
            logger.error(f"Error setting taskbar icon with window handle: {e}")
    
    # Show ExifTool status after window is visible
    if is_available:
        show_exiftool_success_status(window, version)
    else:
        show_exiftool_error_dialog(error_msg)
    
    # Load last file if available
    if config.selected_file and os.path.exists(config.selected_file):
        window.load_file(config.selected_file)
    
    # Run the application
    try:
        return app.exec()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        app.quit()
        return 0

if __name__ == "__main__":
    sys.exit(main())

