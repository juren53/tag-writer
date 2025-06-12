#!/usr/bin/python3
"""
Image viewer module for tag-writer application.

This module provides a UI component for displaying images and thumbnails.
"""

import os
import logging
import wx

from tag_writer.utils.image_processing import load_image, create_thumbnail, pil_to_wx_image

logger = logging.getLogger(__name__)

class ImageViewer(wx.Panel):
    """
    Panel for displaying and interacting with images.
    
    Features:
    - Thumbnail preview
    - Full image viewing
    - Zoom in/out functionality
    """
    
    def __init__(self, parent):
        """
        Initialize the image viewer panel.
        
        Args:
            parent: Parent window
        """
        super().__init__(parent, style=wx.BORDER_SUNKEN)
        
        # Initialize state
        self.current_image_path = None
        self.pil_image = None
        self.zoom_factor = 1.0
        self.dimensions_label = None
        
        # Setup UI
        self.setup_ui()
        
        # Bind events
        self.Bind(wx.EVT_SIZE, self.on_size)
        
        logger.info("Image viewer initialized")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Image panel (with border and background color)
        self.image_panel = wx.Panel(self, style=wx.BORDER_SUNKEN)
        self.image_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Thumbnail text
        self.thumbnail_text = wx.StaticText(
            self.image_panel,
            label="No image loaded",
            style=wx.ALIGN_CENTER
        )
        self.thumbnail_text.SetForegroundColour(wx.Colour(100, 100, 100))
        self.thumbnail_text.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Image sizer
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        self.image_sizer.Add(self.thumbnail_text, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Create StaticBitmap for the thumbnail
        self.thumbnail_bitmap = wx.StaticBitmap(self.image_panel, wx.ID_ANY, wx.NullBitmap)
        self.image_sizer.Add(self.thumbnail_bitmap, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Set image panel sizer
        self.image_panel.SetSizer(self.image_sizer)
        
        # Button to view full image
        self.btn_view_full = wx.Button(self, label="View Full Image")
        self.btn_view_full.Bind(wx.EVT_BUTTON, self.on_view_full)
        
        # Create dimensions label
        self.dimensions_label = wx.StaticText(self, label="Dimensions: --", style=wx.ALIGN_CENTER_HORIZONTAL)
        self.dimensions_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        # Add image panel to main sizer
        self.main_sizer.Add(self.image_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # Add view full button and dimensions label after the image panel
        self.main_sizer.Add(self.btn_view_full, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        self.main_sizer.Add(self.dimensions_label, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        
        # Set sizer
        self.SetSizer(self.main_sizer)
        
        logger.info("Image viewer UI setup complete")
    
    def load_image(self, file_path):
        """
        Load and display an image.
        
        Args:
            file_path: Path to the image file
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        try:
            # Load the image using PIL
            self.pil_image = load_image(file_path)
            if not self.pil_image:
                return False
            
            # Store current path
            self.current_image_path = file_path
            
            # Create and display thumbnail
            self.display_thumbnail()
            
            # Update thumbnail text
            file_name = os.path.basename(file_path)
            self.thumbnail_text.SetLabel(file_name)
            
            # Enable view full button
            self.btn_view_full.Enable()
            
            logger.info(f"Loaded image: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading image {file_path}: {e}")
            self.thumbnail_text.SetLabel("Error loading image")
            self.thumbnail_bitmap.SetBitmap(wx.NullBitmap)
            self.btn_view_full.Disable()
            # Reset dimensions label
            self.dimensions_label.SetLabel("Dimensions: --")
            return False
    
    def display_thumbnail(self):
        """Create and display a thumbnail of the current image."""
        if not self.pil_image:
            return
        
        try:
            # Get panel size
            panel_size = self.image_panel.GetSize()
            max_size = min(panel_size.width - 20, panel_size.height - 50)
            thumbnail_size = (max_size, max_size)
            
            # Create thumbnail
            thumbnail = create_thumbnail(self.pil_image, thumbnail_size)
            if not thumbnail:
                return
            
            # Convert to wx.Bitmap and display
            wx_image = pil_to_wx_image(thumbnail)
            if wx_image:
                bitmap = wx.Bitmap(wx_image)
                self.thumbnail_bitmap.SetBitmap(bitmap)
                
                # Update dimensions label with original image size
                if self.pil_image:
                    img_width, img_height = self.pil_image.size
                    dimensions_text = f"Dimensions: {img_width} x {img_height} pixels"
                    self.dimensions_label.SetLabel(dimensions_text)
                
                # Update layout
                self.image_panel.Layout()
            
            logger.info("Displayed thumbnail")
        except Exception as e:
            logger.error(f"Error displaying thumbnail: {e}")
            # Reset dimensions label on error
            self.dimensions_label.SetLabel("Dimensions: --")
    
    def on_size(self, event):
        """Handle resize events."""
        # Redisplay thumbnail when panel is resized
        self.display_thumbnail()
        event.Skip()
    
    def on_view_full(self, event):
        """Handle View Full Image button clicks."""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            wx.MessageBox("No image loaded", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        # Create and show the full image viewer
        from tag_writer.ui.dialogs import FullImageViewer
        viewer = FullImageViewer(self, self.current_image_path)
        viewer.Show()
