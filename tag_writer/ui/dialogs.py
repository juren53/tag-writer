#!/usr/bin/python3
"""
Dialog boxes module for tag-writer application.

This module provides various dialog boxes used in the application:
- Full image viewer
- Tag list viewer
- License information
- Help dialog
"""

import os
import logging
import wx

from tag_writer.utils.image_processing import load_image, pil_to_wx_image, adjust_zoom
from tag_writer.utils.config import config

logger = logging.getLogger(__name__)

class FullImageViewer(wx.Frame):
    """
    Dialog for viewing full-size images with zoom capability.
    """
    
    def __init__(self, parent, image_path):
        """
        Initialize the full image viewer.
        
        Args:
            parent: Parent window
            image_path: Path to the image file to display
        """
        super().__init__(
            parent,
            title=f"Image Viewer - {os.path.basename(image_path)}",
            size=(800, 600),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # Store image info
        self.image_path = image_path
        self.original_image = None
        self.zoomed_image = None
        self.zoom_factor = 1.0
        
        # Setup UI
        self.setup_ui()
        
        # Load the image
        self.load_image()
        
        # Center on screen
        self.Centre()
        
        # Bind events
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        
        logger.info(f"Full image viewer initialized for {image_path}")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main panel and sizer
        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create a scrolled window for the image
        self.scroll_window = wx.ScrolledWindow(
            self.main_panel,
            style=wx.HSCROLL | wx.VSCROLL
        )
        self.scroll_window.SetBackgroundColour(wx.Colour(240, 240, 240))
        
        # Panel for the image
        self.image_panel = wx.Panel(self.scroll_window)
        self.image_bitmap = wx.StaticBitmap(self.image_panel, wx.ID_ANY, wx.NullBitmap)
        
        # Image sizer
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        self.image_sizer.Add(self.image_bitmap, 0, wx.ALL, 10)
        self.image_panel.SetSizer(self.image_sizer)
        
        # Scroll window sizer
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_sizer.Add(self.image_panel, 0, wx.EXPAND)
        self.scroll_window.SetSizer(self.scroll_sizer)
        
        # Controls panel
        self.controls_panel = wx.Panel(self.main_panel)
        self.controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Zoom out button
        self.zoom_out_btn = wx.Button(self.controls_panel, label="Zoom Out (-)")
        self.zoom_out_btn.Bind(wx.EVT_BUTTON, self.on_zoom_out)
        self.controls_sizer.Add(self.zoom_out_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Zoom text
        self.zoom_text = wx.StaticText(self.controls_panel, label="Zoom: 100%")
        self.controls_sizer.Add(self.zoom_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Zoom in button
        self.zoom_in_btn = wx.Button(self.controls_panel, label="Zoom In (+)")
        self.zoom_in_btn.Bind(wx.EVT_BUTTON, self.on_zoom_in)
        self.controls_sizer.Add(self.zoom_in_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Reset zoom button
        self.reset_zoom_btn = wx.Button(self.controls_panel, label="Reset Zoom (0)")
        self.reset_zoom_btn.Bind(wx.EVT_BUTTON, self.on_reset_zoom)
        self.controls_sizer.Add(self.reset_zoom_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # File info text
        self.file_info = wx.StaticText(self.controls_panel, label="")
        self.controls_sizer.Add(self.file_info, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Close button
        self.close_btn = wx.Button(self.controls_panel, wx.ID_CLOSE, "Close")
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        self.controls_sizer.Add(self.close_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.controls_panel.SetSizer(self.controls_sizer)
        
        # Add panels to main sizer
        self.main_sizer.Add(self.scroll_window, 1, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.controls_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        # Set main panel sizer
        self.main_panel.SetSizer(self.main_sizer)
        
        logger.info("Full image viewer UI setup complete")
    
    def load_image(self):
        """Load and display the image."""
        try:
            # Load image with PIL
            self.original_image = load_image(self.image_path)
            if not self.original_image:
                wx.MessageBox("Failed to load image", "Error", wx.OK | wx.ICON_ERROR)
                self.Close()
                return
            
            # Store globally for potential later use
            config.original_image = self.original_image
            
            # Display image at current zoom
            self.update_display()
            
            # Update file info
            width, height = self.original_image.size
            self.file_info.SetLabel(f"Size: {width}x{height}")
            
            logger.info(f"Loaded image in viewer: {self.image_path}")
        except Exception as e:
            logger.error(f"Error loading image in viewer: {e}")
            wx.MessageBox(f"Error loading image: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
            self.Close()
    
    def update_display(self):
        """Update the displayed image based on current zoom factor."""
        if not self.original_image:
            return
        
        try:
            # Adjust zoom
            self.zoomed_image = adjust_zoom(self.original_image, self.zoom_factor)
            if not self.zoomed_image:
                return
            
            # Convert to wx.Bitmap and display
            wx_image = pil_to_wx_image(self.zoomed_image)
            if wx_image:
                bitmap = wx.Bitmap(wx_image)
                self.image_bitmap.SetBitmap(bitmap)
                
                # Update zoom text
                zoom_percent = int(self.zoom_factor * 100)
                self.zoom_text.SetLabel(f"Zoom: {zoom_percent}%")
                
                # Update layout
                self.image_panel.Layout()
                self.scroll_window.SetVirtualSize(self.image_panel.GetSize())
                self.scroll_window.SetScrollRate(20, 20)
                
            logger.info(f"Updated image display with zoom factor {self.zoom_factor}")
        except Exception as e:
            logger.error(f"Error updating image display: {e}")
    
    def on_zoom_in(self, event):
        """Handle zoom in button clicks."""
        self.zoom_factor *= 1.25
        self.update_display()
    
    def on_zoom_out(self, event):
        """Handle zoom out button clicks."""
        self.zoom_factor *= 0.8
        self.update_display()
    
    def on_reset_zoom(self, event):
        """Handle reset zoom button clicks."""
        self.zoom_factor = 1.0
        self.update_display()
    
    def on_close(self, event):
        """Handle close button clicks."""
        self.Close()
    
    def on_key(self, event):
        """Handle keyboard events."""
        key_code = event.GetKeyCode()
        
        if key_code == ord('+') or key_code == wx.WXK_ADD:
            self.on_zoom_in(event)
        elif key_code == ord('-') or key_code == wx.WXK_SUBTRACT:
            self.on_zoom_out(event)
        elif key_code == ord('0'):
            self.on_reset_zoom(event)
        elif key_code == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()

class TagListViewer(wx.Dialog):
    """
    Dialog for viewing all metadata tags in an image.
    """
    
    def __init__(self, parent, metadata):
        """
        Initialize the tag list viewer.
        
        Args:
            parent: Parent window
            metadata: Dictionary of metadata tags
        """
        super().__init__(
            parent,
            title="All Metadata Tags",
            size=(600, 500),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # Store metadata
        self.metadata = metadata
        
        # Setup UI
        self.setup_ui()
        
        # Center on screen
        self.Centre()
        
        logger.info("Tag list viewer initialized")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main panel and sizer
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header text
        header = wx.StaticText(panel, label="All Metadata Tags")
        header_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        header.SetFont(header_font)
        sizer.Add(header, 0, wx.ALL | wx.EXPAND, 10)
        
        # Create list control
        self.tag_list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        
        # Add columns
        self.tag_list.InsertColumn(0, "Tag Name", width=200)
        self.tag_list.InsertColumn(1, "Value", width=350)
        
        # Add tags to list
        self.populate_tags()
        
        sizer.Add(self.tag_list, 1, wx.ALL | wx.EXPAND, 10)
        
        # Search panel
        search_panel = wx.Panel(panel)
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        search_label = wx.StaticText(search_panel, label="Search:")
        search_sizer.Add(search_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.search_field = wx.TextCtrl(search_panel)
        self.search_field.Bind(wx.EVT_TEXT, self.on_search)
        search_sizer.Add(self.search_field, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        search_panel.SetSizer(search_sizer)
        sizer.Add(search_panel, 0, wx.ALL | wx.EXPAND, 5)
        
        # Buttons
        button_panel = wx.Panel(panel)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        copy_btn = wx.Button(button_panel, label="Copy Selected")
        copy_btn.Bind(wx.EVT_BUTTON, self.on_copy)
        button_sizer.Add(copy_btn, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        close_btn = wx.Button(button_panel, wx.ID_CLOSE, "Close")
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        button_sizer.Add(close_btn, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        button_panel.SetSizer(button_sizer)
        sizer.Add(button_panel, 0, wx.ALL | wx.EXPAND, 5)
        
        # Set panel sizer
        panel.SetSizer(sizer)
        
        logger.info("Tag list viewer UI setup complete")
    
    def populate_tags(self, filter_text=None):
        """
        Populate the tag list with metadata.
        
        Args:
            filter_text: Optional text to filter tags by
        """
        # Clear existing items
        self.tag_list.DeleteAllItems()
        
        # Add metadata to list
        index = 0
        for key, value in sorted(self.metadata.items()):
            # Skip binary data
            if isinstance(value, bytes):
                value = "<binary data>"
            
            # Convert value to string
            if not isinstance(value, str):
                value = str(value)
            
            # Apply filter if provided
            if filter_text and filter_text.lower() not in key.lower() and filter_text.lower() not in value.lower():
                continue
            
            # Add to list
            item_index = self.tag_list.InsertItem(index, key)
            self.tag_list.SetItem(item_index, 1, value)
            index += 1
        
        # Auto-size columns
        self.tag_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.tag_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        
        logger.info(f"Populated tag list with {index} items")
    
    def on_search(self, event):
        """Handle search field changes."""
        filter_text = self.search_field.GetValue()
        self.populate_tags(filter_text)
    
    def on_copy(self, event):
        """Handle copy button clicks."""
        selected = self.tag_list.GetFirstSelected()
        if selected == -1:
            wx.MessageBox("No tag selected", "Info", wx.OK | wx.ICON_INFORMATION)
            return
        
        # Get tag and value
        tag = self.tag_list.GetItemText(selected, 0)
        value = self.tag_list.GetItemText(selected, 1)
        
        # Copy to clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(f"{tag}: {value}"))
            wx.TheClipboard.Close()
            wx.MessageBox("Copied to clipboard", "Info", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Failed to copy to clipboard", "Error", wx.OK | wx.ICON_ERROR)
    
    def on_close(self, event):
        """Handle close button clicks."""
        self.EndModal(wx.ID_CLOSE)
