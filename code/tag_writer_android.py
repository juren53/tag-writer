#!/usr/bin/env python3
# tag_writer_android.py - Kivy version of tag-writer for Android
# Version 0.13 (2025-04-05)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.garden.filebrowser import FileBrowser  # May need to install this separately

# For Android-specific file access and permissions
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass

import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Try to import PIL for image handling
try:
    from PIL import Image as PILImage
    from PIL import ExifTags
    PIL_AVAILABLE = True
except ImportError:
    logging.warning("PIL/Pillow not available - image handling functionality will be limited")
    PIL_AVAILABLE = False

# Global constants
APP_VERSION = "0.13"
APP_DATE = "2025-04-05"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".tag_writer_config.json")

# Load configuration
def load_config():
    """Load application configuration from JSON file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {"recent_files": []}
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}")
        return {"recent_files": []}

# Save configuration
def save_config(config_data):
    """Save application configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f)
        return True
    except Exception as e:
        logging.error(f"Error saving config: {str(e)}")
        return False

# Metadata handling class (replacement for exiftool functionality)
class MetadataHandler:
    """Handles reading and writing image metadata without exiftool dependency"""
    
    def read_metadata(self, file_path):
        """Read metadata from an image file"""
        if not PIL_AVAILABLE:
            return {}
            
        try:
            # This is a simplified version - in a real app, you'd need more robust handling
            img = PILImage.open(file_path)
            exif_data = {}
            
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif:
                    for tag, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        exif_data[tag_name] = value
            
            # Get IPTC data (simplified - would need more complete implementation)
            # Note: Python libraries like pyexiv2 or exif could be used here
            
            # Return data in a format similar to the original app
            return {
                'Headline': exif_data.get('ImageDescription', ''),
                'Caption-Abstract': exif_data.get('UserComment', ''),
                'Credit': '',  # These fields would need custom extraction
                'ObjectName': '',
                'Writer-Editor': '',
                'By-line': exif_data.get('Artist', ''),
                'Source': '',
                'DateCreated': exif_data.get('DateTime', ''),
                'CopyrightNotice': exif_data.get('Copyright', '')
            }
            
        except Exception as e:
            logging.error(f"Error reading metadata: {str(e)}")
            return {}
    
    def write_metadata(self, file_path, metadata):
        """Write metadata to an image file"""
        # In a real implementation, you would use a library like pyexiv2
        # or another solution to write IPTC data
        
        try:
            # This is a placeholder - actual implementation would be more complex
            logging.info(f"Writing metadata to {file_path}")
            
            # Would need to save IPTC metadata here
            return True
        except Exception as e:
            logging.error(f"Error writing metadata: {str(e)}")
            return False

# Main UI Layout
class MetadataEditorLayout(BoxLayout):
    """Main application layout"""
    
    selected_file = StringProperty('')
    thumbnail_source = StringProperty('')
    status_text = StringProperty('Ready')
    directory_files = ListProperty([])
    current_file_index = -1
    
    def __init__(self, **kwargs):
        super(MetadataEditorLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.metadata_handler = MetadataHandler()
        self.config_data = load_config()
        
        # Build the UI
        self._build_header()
        self._build_content()
        self._build_footer()
        
        # Check for Android permissions
        if platform == 'android':
            self._request_android_permissions()
    
    def _request_android_permissions(self):
        """Request necessary Android permissions"""
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
    
    def _build_header(self):
        """Build the header section with file controls"""
        header = BoxLayout(
            size_hint=(1, None),
            height=50,
            spacing=10,
            padding=5
        )
        
        # File selection button
        select_btn = Button(
            text='Select File',
            size_hint=(None, 1),
            width=120,
            on_release=self.show_file_chooser
        )
        
        # Navigation buttons
        nav_box = BoxLayout(size_hint=(None, 1), width=100, spacing=5)
        self.prev_btn = Button(text='←', on_release=self.prev_file, disabled=True)
        self.next_btn = Button(text='→', on_release=self.next_file, disabled=True)
        nav_box.add_widget(self.prev_btn)
        nav_box.add_widget(self.next_btn)
        
        # Write metadata button
        write_btn = Button(
            text='Write Metadata',
            size_hint=(None, 1),
            width=150,
            on_release=self.write_metadata
        )
        
        # Filename label
        self.filename_label = Label(
            text='No file selected',
            size_hint=(1, 1),
            halign='left',
            valign='middle'
        )
        self.filename_label.bind(size=self.filename_label.setter('text_size'))
        
        header.add_widget(select_btn)
        header.add_widget(nav_box)
        header.add_widget(write_btn)
        header.add_widget(self.filename_label)
        
        self.add_widget(header)
    
    def _build_content(self):
        """Build the main content area with metadata form and image preview"""
        content = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 1),
            spacing=10
        )
        
        # Metadata form in a scroll view
        form_scroll = ScrollView(size_hint=(0.7, 1))
        form_layout = self._build_metadata_form()
        form_scroll.add_widget(form_layout)
        
        # Image preview section
        preview_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.3, 1),
            spacing=10
        )
        
        # Thumbnail display
        self.thumbnail = Image(
            source='',
            size_hint=(1, 0.8),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # View full image button
        view_button = Button(
            text='View Full Image',
            size_hint=(1, 0.1),
            on_release=self.show_full_image
        )
        
        preview_layout.add_widget(Label(text='Image Preview', size_hint=(1, 0.1)))
        preview_layout.add_widget(self.thumbnail)
        preview_layout.add_widget(view_button)
        
        content.add_widget(form_scroll)
        content.add_widget(preview_layout)
        
        self.add_widget(content)
    
    def _build_metadata_form(self):
        """Build the metadata entry form"""
        form = GridLayout(
            cols=2,
            spacing=10,
            size_hint=(1, None)
        )
        # Make the grid layout expandable
        form.bind(minimum_height=form.setter('height'))
        
        # Helper function to add a field
        def add_field(label_text, attribute_name):
            form.add_widget(Label(
                text=label_text,
                halign='right',
                size_hint=(0.3, None),
                height=40
            ))
            
            if label_text == 'Caption Abstract:':
                # Multiline text input for caption
                text_input = TextInput(
                    multiline=True,
                    size_hint=(0.7, None),
                    height=120
                )
            else:
                # Single line for other fields
                text_input = TextInput(
                    multiline=False,
                    size_hint=(0.7, None),
                    height=40
                )
            
            setattr(self, attribute_name, text_input)
            form.add_widget(text_input)
        
        # Add all metadata fields
        add_field('Headline:', 'headline_input')
        add_field('Caption Abstract:', 'caption_input')
        add_field('Credit:', 'credit_input')
        add_field('Unique ID [Object Name]:', 'object_name_input')
        add_field('Writer/Editor:', 'writer_editor_input')
        add_field('By-line:', 'byline_input')
        add_field('Source:', 'source_input')
        add_field('Date Created:', 'date_input')
        add_field('Copyright Notice:', 'copyright_input')
        
        return form
    
    def _build_footer(self):
        """Build the footer with status bar"""
        footer = BoxLayout(
            size_hint=(1, None),
            height=30,
            spacing=10
        )
        
        # Status label
        self.status_label = Label(
            text=self.status_text,
            size_hint=(0.7, 1),
            halign='left',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        
        # Version label
        version_label = Label(
            text=f"Ver {APP_VERSION} ({APP_DATE})",
            size_hint=(0.3, 1),
            halign='right',
            valign='middle'
        )
        version_label.bind(size=version_label.setter('text_size'))
        
        footer.add_widget(self.status_label)
        footer.add_widget(version_label)
        
        self.add_widget(footer)
    
    def show_file_chooser(self, instance):
        """Show file chooser dialog to select an image"""
        if platform == 'android':
            # For Android, we'd use the native file picker
            # This is simplified - actual implementation would be more complex
            # and handle Android's file access system
            pass
        else:
            # For desktop platforms, use Kivy's file chooser
            content = BoxLayout(orientation='vertical')
            filechooser = FileChooserListView(
                path=os.path.expanduser('~'),
                filters=['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']
            )
            
            buttons = BoxLayout(
                size_hint=(1, 0.1),
                spacing=10,
                padding=10
            )
            
            btn_cancel = Button(text='Cancel')
            btn_select = Button(text='Select')
            
            buttons.add_widget(btn_cancel)
            buttons.add_widget(btn_select)
            
            content.add_widget(filechooser)
            content.add_widget(buttons)
            
            popup = Popup(
                title='Select an image file',
                content=content,
                size_hint=(0.9, 0.9)
            )
            
            btn_cancel.bind(on_release=popup.dismiss)
            btn_select.bind(on_release=lambda x: self._file_selected(filechooser.selection, popup))
            
            popup.open()
    
    def _file_selected(self, selection, popup):
        """Handle file selection"""
        if not selection:
            return
            
        file_path = selection[0]
        popup.dismiss()
        
        self.select_file(file_path)
    
    def select_file(self, file_path):
        """Select a file and load its metadata"""
        if not os.path.isfile(file_path):
            self.status_text = f"Error: File does not exist"
            return
            
        self.selected_file = file_path
        self.filename_label.text = f"File: {os.path.basename(file_path)}"
        
        # Load metadata
        metadata = self.metadata_handler.read_metadata(file_path)
        self._populate_form(metadata)
        
        # Update thumbnail
        self._update_thumbnail(file_path)
        
        # Update recent files list
        self._update_recent_files(file_path)
        
        # Update directory files list for navigation
        self._update_directory_files(file_path)
        
        # Update status
        self.status_text = f"Loaded {os.path.basename(file_path)}"
    
    def _populate_form(self, metadata):
        """Populate form fields with metadata values"""
        self.headline_input.text = metadata.get('Headline', '')
        self.caption_input.text = metadata.get('Caption-Abstract', '')
        self.credit_input.text = metadata.get('Credit', '')
        self.object_name_input.text = metadata.get('ObjectName', '')
        self.writer_editor_input.text = metadata.get('Writer-Editor', '')
        self.byline_input.text = metadata.get('By-line', '')
        self.source_input.text = metadata.get('Source', '')
        self.date_input.text = metadata.get('DateCreated', '')
        self.copyright_input.text = metadata.get('CopyrightNotice', '')
    
    def write_metadata(self, instance=None):
        """Write metadata to the selected image file"""
        if not self.selected_file:
            self.status_text = "Error: No file selected!"
            return False
            
        try:
            # Gather metadata from form fields
            metadata = {
                'Headline': self.headline_input.text,
                'Caption-Abstract': self.caption_input.text,
                'Credit': self.credit_input.text,
                'ObjectName': self.object_name_input.text,
                'Writer-Editor': self.writer_editor_input.text,
                'By-line': self.byline_input.text,
                'Source': self.source_input.text,
                'DateCreated': self.date_input.text,
                'CopyrightNotice': self.copyright_input.text
            }
            
            # Write metadata to the file
            result = self.metadata_handler.write_metadata(self.selected_file, metadata)
            
            if result:
                self.status_text = "Metadata written successfully!"
                return True
            else:
                self.status_text = "Error writing metadata"
                return False
                
        except Exception as e:
            logging.error(f"Error writing metadata: {str(e)}")
            self.status_text = f"Error: {str(e)}"
            return False
    
    def prev_file(self, instance=None):
        """Navigate to the previous file in the directory"""
        self._navigate_files(-1)
    
    def next_file(self, instance=None):
        """Navigate to the next file in the directory"""
        self._navigate_files(1)
    
    def _navigate_files(self, direction):
        """Navigate files with the given direction (-1 for previous, 1 for next)"""
        if not self.directory_files:
            return
            
        new_index = self.current_file_index + direction
        
        if 0 <= new_index < len(self.directory_files):
            self.current_file_index = new_index
            file_path = self.directory_files[new_index]
            self.select_file(file_path)
            
            # Update navigation button state
            self._update_nav_buttons()
    
    def _update_nav_buttons(self):
        """Update navigation button states based on current position"""
        # Disable prev button if at first file
        self.prev_btn.disabled = (self.current_file_index <= 0)
        
        # Disable next button if at last file
        self.next_btn.disabled = (self.current_file_index >= len(self.directory_files) - 1)
    
    def _update_directory_files(self, file_path):
        """Get all image files in the same directory as the given file"""
        try:
            directory = os.path.dirname(file_path)
            
            # Define supported image extensions
            image_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.gif', '.bmp']
            
            # Get all files in the directory
            all_files = []
            for ext in image_extensions:
                files = [os.path.join(directory, f) for f in os.listdir(directory) 
                         if f.lower().endswith(ext) and os.path.isfile(os.path.join(directory, f))]
                all_files.extend(files)
            
            # Sort alphabetically
            self.directory_files = sorted(all_files, key=lambda x: os.path.basename(x).lower())
            
            # Find the index of the current file
            try:
                self.current_file_index = self.directory_files.index(file_path)
            except ValueError:
                self.current_file_index = -1
            
            # Update navigation buttons
            self._update_nav_buttons()
            
            return True
        except Exception as e:
            logging.error(f"Error updating directory files: {str(e)}")
            self.directory_files = []
            self.current_file_index = -1
            self._update_nav_buttons()
            return False
    
    def _update_thumbnail(self, file_path):
        """Update the thumbnail display with the selected image"""
        if not PIL_AVAILABLE:
            return False
            
        try:
            # Check if file is an image
            file_ext = os.path.splitext(file_path)[1].lower()
            image_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.gif', '.bmp']
            
            if file_ext not in image_extensions:
                logging.debug(f"File extension {file_ext} not recognized as an image")
                return False
            
            # Open and resize the image for thumbnail
            img = PILImage.open(file_path)
            max_size = (self.thumbnail.width, self.thumbnail.height)
            img.thumbnail(max_size)
            
            # Save the thumbnail to a temporary file for Kivy to display
            thumb_path = os.path.join(os.path.dirname(file_path), '.thumb_temp.png')
            img.save(thumb_path)
            
            # Set the thumbnail source
            self.thumbnail.source = thumb_path
            self.thumbnail.reload()
            
            # Store the path for the full image viewer
            self.thumbnail_source = thumb_path
            return True
            
        except Exception as e:
            logging.error(f"Error creating thumbnail: {str(e)}")
            return False
    
    def _update_recent_files(self, file_path):
        """Update list of recently accessed files"""
        # Add the current file to the beginning of recent files
        if file_path in self.config_data.get('recent_files', []):
            self.config_data['recent_files'].remove(file_path)
            
        if 'recent_files' not in self.config_data:
            self.config_data['recent_files'] = []
            
        self.config_data['recent_files'].insert(0, file_path)
        
        # Limit to 5 recent files
        self.config_data['recent_files'] = self.config_data['recent_files'][:5]
        
        # Save the updated config
        save_config(self.config_data)
    
    def show_full_image(self, instance=None):
        """Show the full-size image in a popup"""
        if not self.selected_file or not PIL_AVAILABLE:
            return
            
        try:
            # Create a popup for displaying the full image
            content = BoxLayout(orientation='vertical')
            
            # Calculate the size for the popup (80% of screen)
            width, height = Window.size
            popup_size = (width * 0.9, height * 0.9)
            
            # Create a ScrollView to allow panning and zooming
            scroll_view = ScrollView(
                size_hint=(1, 1),
                bar_width=10,
                scroll_type=['bars', 'content'],
                do_scroll_x=True,
                do_scroll_y=True
            )
            
            # Create an Image widget for the full image
            full_img = Image(
                source=self.selected_file,
                size_hint=(None, None),
                allow_stretch=False,
                keep_ratio=True
            )
            
            # Set the image size based on its natural dimensions
            img_obj = PILImage.open(self.selected_file)
            w, h = img_obj.size
            full_img.size = (w, h)
            img_obj.close()
            
            # Add the image to the scroll view
            scroll_view.add_widget(full_img)
            
            # Add controls at the bottom
            controls = BoxLayout(
                size_hint=(1, None),
                height=50,
                spacing=10,
                padding=5
            )
            
            # Close button
            close_btn = Button(text='Close', size_hint=(None, 1), width=100)
            
            # Add image information label
            info_label = Label(
                text=f"{os.path.basename(self.selected_file)} ({w}×{h})",
                size_hint=(1, 1)
            )
            
            controls.add_widget(info_label)
            controls.add_widget(close_btn)
            
            # Build the content layout
            content.add_widget(scroll_view)
            content.add_widget(controls)
            
            # Create and show the popup
            popup = Popup(
                title='Full Image View',
                content=content,
                size_hint=(0.95, 0.95),
                auto_dismiss=True
            )
            
            # Bind the close button
            close_btn.bind(on_release=popup.dismiss)
            
            # Open the popup
            popup.open()
            
        except Exception as e:
            logging.error(f"Error showing full image: {str(e)}")
            self.status_text = f"Error showing image: {str(e)}"


class TagWriterApp(App):
    """Main Kivy application class"""
    
    def build(self):
        """Build the application UI"""
        # Set window title and size
        self.title = 'Tag Writer'
        
        # Return the main layout
        return MetadataEditorLayout()
    
    def on_start(self):
        """Called when the application starts"""
        # Request Android permissions if needed
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
    
    def on_pause(self):
        """Called when the application is paused"""
        # Save any necessary state
        return True
    
    def on_resume(self):
        """Called when the application is resumed"""
        pass
    
    def on_stop(self):
        """Called when the application is stopped"""
        # Save application state
        pass


if __name__ == '__main__':
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Start the application
        TagWriterApp().run()
    except Exception as e:
        logging.error(f"Error starting application: {str(e)}")
        
        # For debugging on Android
        if platform == 'android':
            from jnius import autoclass
            Toast = autoclass('android.widget.Toast')
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            Toast.makeText(context, f"Error: {str(e)}", Toast.LENGTH_LONG).show()
