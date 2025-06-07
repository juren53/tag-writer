#!/usr/bin/python3
"""
Metadata panel module for tag-writer application.

This module provides a UI component for editing image metadata.
"""

import logging
import wx
import wx.richtext
import datetime

from tag_writer.models.metadata import MetadataManager

logger = logging.getLogger(__name__)

class MetadataPanel(wx.Panel):
    """
    Panel for displaying and editing image metadata.
    
    This panel provides form fields for common metadata fields
    and handles interactions with the metadata manager.
    """
    
    def __init__(self, parent, metadata_manager):
        """
        Initialize the metadata panel.
        
        Args:
            parent: Parent window
            metadata_manager: MetadataManager instance
        """
        super().__init__(parent, style=wx.BORDER_SUNKEN)
        
        # Store reference to metadata manager
        self.metadata_manager = metadata_manager
        
        # Character counter for caption field
        self.char_count_text = None
        self.max_caption_chars = 1000
        self._last_styled_length = 0  # Track last styled length
        
        # Constant for label width
        self.LABEL_MIN_WIDTH = 120
        
        # Setup UI
        self.setup_ui()
        
        # Set initial state
        self.update_from_manager()
        
        logger.info("Metadata panel initialized")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(self, label="Image Metadata")
        title_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        self.main_sizer.Add(title, 0, wx.ALL | wx.EXPAND, 5)
        
        # Create scrollable area for fields
        self.scroll = wx.ScrolledWindow(self)
        self.scroll.SetScrollRate(0, 20)  # Increase vertical scroll rate
        self.field_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create a panel to hold all fields with fixed min width
        self.fields_panel = wx.Panel(self.scroll)
        self.fields_panel.SetMinSize((350, -1))  # Set minimum width
        
        # IPTC fields group
        self.create_metadata_fields()
        
        # Write metadata button
        self.btn_write = wx.Button(self, label="Write Metadata")
        self.btn_write.Bind(wx.EVT_BUTTON, self.on_write)
        self.main_sizer.Add(self.btn_write, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        # Set scrolled window sizer
        self.scroll.SetSizer(self.field_sizer)
        
        # Add scroll panel to main sizer
        self.main_sizer.Add(self.scroll, 1, wx.EXPAND | wx.ALL, 5)
        
        # Set panel sizer
        self.SetSizer(self.main_sizer)
        
        logger.info("Metadata panel UI setup complete")
    
    def create_metadata_fields(self):
        """Create UI elements for metadata fields."""
        # Title and description section
        title_box = wx.StaticBox(self.fields_panel, label="Title & Description")
        title_sizer = wx.StaticBoxSizer(title_box, wx.VERTICAL)
        
        # Grid for form fields
        grid = wx.GridBagSizer(10, 10)  # Increase spacing for better readability at high zoom
        grid.SetMinSize((350, -1))  # Set minimum width for the grid
        current_row = 0
        
        # Create a utility function for label creation with consistent styling
        def create_label(parent, text):
            label = wx.StaticText(parent, label=text)
            label.SetMinSize((self.LABEL_MIN_WIDTH, -1))
            # Allow labels to wrap if needed at high zoom levels
            label.Wrap(self.LABEL_MIN_WIDTH)
            return label
        
        # Headline field
        headline_label = create_label(self.fields_panel, "Headline:")
        grid.Add(headline_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.headline_field = wx.TextCtrl(self.fields_panel)
        grid.Add(self.headline_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Object Name field
        obj_name_label = create_label(self.fields_panel, "Object Name:")
        grid.Add(obj_name_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.object_name_field = wx.TextCtrl(self.fields_panel)
        grid.Add(self.object_name_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Caption/Description field
        caption_label = create_label(self.fields_panel, "Caption Abstract:")
        grid.Add(caption_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.RIGHT, border=10)
        
        # Rich text for caption
        caption_panel = wx.Panel(self.fields_panel)
        caption_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.caption_field = wx.richtext.RichTextCtrl(
            caption_panel, style=wx.richtext.RE_MULTILINE, size=(-1, 100)
        )
        # Set default text color to white
        self.caption_field.SetDefaultStyle(wx.TextAttr(wx.WHITE))
        
        caption_sizer.Add(self.caption_field, 1, wx.EXPAND)
        
        # Character count display
        char_count_panel = wx.Panel(caption_panel)
        char_count_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.char_count_text = wx.StaticText(
            char_count_panel, 
            label=f"0/{self.max_caption_chars} characters"
        )
        info_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.char_count_text.SetFont(info_font)
        
        char_count_sizer.Add(self.char_count_text, 0, wx.ALIGN_RIGHT)
        char_count_panel.SetSizer(char_count_sizer)
        
        caption_sizer.Add(char_count_panel, 0, wx.ALIGN_RIGHT | wx.TOP, 2)
        
        caption_panel.SetSizer(caption_sizer)
        grid.Add(caption_panel, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Make columns expandable
        grid.AddGrowableCol(1)
        
        title_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)
        self.field_sizer.Add(title_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Creator information section
        creator_box = wx.StaticBox(self.fields_panel, label="Creator Information")
        creator_sizer = wx.StaticBoxSizer(creator_box, wx.VERTICAL)
        
        creator_grid = wx.GridBagSizer(10, 10)  # Increased spacing
        creator_grid.SetMinSize((350, -1))  # Set minimum width for the grid
        current_row = 0
        
        # By-line (Creator) field
        byline_label = create_label(self.fields_panel, "By-line:")
        creator_grid.Add(byline_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.creator_field = wx.TextCtrl(self.fields_panel)
        creator_grid.Add(self.creator_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # By-line Title field
        byline_title_label = create_label(self.fields_panel, "By-line Title:")
        creator_grid.Add(byline_title_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.creator_title_field = wx.TextCtrl(self.fields_panel)
        creator_grid.Add(self.creator_title_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Writer-Editor field
        writer_label = create_label(self.fields_panel, "Writer/Editor:")
        creator_grid.Add(writer_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.writer_editor_field = wx.TextCtrl(self.fields_panel)
        creator_grid.Add(self.writer_editor_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Make columns expandable
        creator_grid.AddGrowableCol(1)
        
        creator_sizer.Add(creator_grid, 0, wx.EXPAND | wx.ALL, 5)
        self.field_sizer.Add(creator_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Source information section
        source_box = wx.StaticBox(self.fields_panel, label="Source Information")
        source_sizer = wx.StaticBoxSizer(source_box, wx.VERTICAL)
        
        source_grid = wx.GridBagSizer(10, 10)  # Increased spacing
        source_grid.SetMinSize((350, -1))  # Set minimum width for the grid
        current_row = 0
        
        # Credit field
        credit_label = create_label(self.fields_panel, "Credit:")
        source_grid.Add(credit_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.credit_field = wx.TextCtrl(self.fields_panel)
        source_grid.Add(self.credit_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Source field
        source_label = create_label(self.fields_panel, "Source:")
        source_grid.Add(source_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.source_field = wx.TextCtrl(self.fields_panel)
        source_grid.Add(self.source_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Date Created field
        date_label = create_label(self.fields_panel, "Date Created:")
        source_grid.Add(date_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.date_field = wx.TextCtrl(self.fields_panel)
        source_grid.Add(self.date_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Make columns expandable
        source_grid.AddGrowableCol(1)
        
        source_sizer.Add(source_grid, 0, wx.EXPAND | wx.ALL, 5)
        self.field_sizer.Add(source_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Copyright section
        copyright_box = wx.StaticBox(self.fields_panel, label="Copyright Information")
        copyright_sizer = wx.StaticBoxSizer(copyright_box, wx.VERTICAL)
        
        copyright_grid = wx.GridBagSizer(10, 10)  # Increased spacing
        copyright_grid.SetMinSize((350, -1))  # Set minimum width for the grid
        current_row = 0
        
        # Copyright field
        copyright_label = create_label(self.fields_panel, "Copyright Notice:")
        copyright_grid.Add(copyright_label, (current_row, 0), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
        self.copyright_field = wx.TextCtrl(self.fields_panel)
        copyright_grid.Add(self.copyright_field, (current_row, 1), (1, 3), flag=wx.EXPAND)
        current_row += 1
        
        # Make columns expandable
        copyright_grid.AddGrowableCol(1)
        
        copyright_sizer.Add(copyright_grid, 0, wx.EXPAND | wx.ALL, 5)
        self.field_sizer.Add(copyright_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # Add fields panel to scroll window
        fields_main_sizer = wx.BoxSizer(wx.VERTICAL)
        fields_main_sizer.Add(self.fields_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.fields_panel.SetSizer(fields_main_sizer)
        
        # Add fields panel to scroll window
        self.field_sizer.Add(self.fields_panel, 1, wx.EXPAND)
        self.scroll.SetSizer(self.field_sizer)
        
        # Bind events
        self.caption_field.Bind(wx.EVT_TEXT, self.on_caption_text)
        
        logger.info("Created metadata field UI elements")
    
    def on_caption_text(self, event):
        """Handle text changes in the caption field."""
        if self.char_count_text:
            text = self.caption_field.GetValue()
            current_length = len(text)
            
            # Update character count display
            self.char_count_text.SetLabel(f"{current_length}/{self.max_caption_chars} characters")
            
            # Change color if over the limit
            if current_length > self.max_caption_chars:
                self.char_count_text.SetForegroundColour(wx.Colour(255, 0, 0))  # Red
            else:
                self.char_count_text.SetForegroundColour(wx.Colour(0, 0, 0))  # Black
            
            # Apply yellow highlighting for text over 256 characters
            # First, reset any existing styling
            self.caption_field.SetDefaultStyle(wx.TextAttr(wx.WHITE))
            
            # Create text attributes for default (white) and exceeded (yellow) text
            default_attr = wx.richtext.RichTextAttr()
            default_attr.SetTextColour(wx.WHITE)
            
            exceeded_attr = wx.richtext.RichTextAttr()
            exceeded_attr.SetTextColour(wx.YELLOW)
            
            # If text is longer than 256 characters, color the excess in yellow
            if current_length > 256:
                # Only apply styling if we're not already past 256 chars or the length crosses the 256 threshold
                if self._last_styled_length <= 256 or current_length != self._last_styled_length:
                    # Apply white color to first 256 characters and yellow to the rest
                    self.caption_field.SetStyle(0, 256, default_attr)
                    self.caption_field.SetStyle(256, current_length, exceeded_attr)
            elif self._last_styled_length > 256:
                # We've gone back below 256 chars, need to reset styling to all white
                self.caption_field.SetStyle(0, current_length, default_attr)
            
            # Store the current length for next time
            self._last_styled_length = current_length
        
        # Only skip if event is not None
        if event:
            event.Skip()
    
    def update_from_manager(self):
        """Update the UI with values from the metadata manager."""
        # Get values from metadata manager
        headline = self.metadata_manager.get_field("Headline", "")
        object_name = self.metadata_manager.get_field("ObjectName", "")
        caption = self.metadata_manager.get_field("Caption-Abstract", "")
        creator = self.metadata_manager.get_field("By-line", "")
        creator_title = self.metadata_manager.get_field("By-lineTitle", "")
        writer_editor = self.metadata_manager.get_field("Writer-Editor", "")
        credit = self.metadata_manager.get_field("Credit", "")
        source = self.metadata_manager.get_field("Source", "")
        date_created = self.metadata_manager.get_field("DateCreated", "")
        copyright_notice = self.metadata_manager.get_field("Copyright", "")
        
        # Update UI fields
        self.headline_field.SetValue(headline)
        self.object_name_field.SetValue(object_name)
        self.caption_field.SetValue(caption)
        self.creator_field.SetValue(creator)
        self.creator_title_field.SetValue(creator_title)
        self.writer_editor_field.SetValue(writer_editor)
        self.credit_field.SetValue(credit)
        self.source_field.SetValue(source)
        self.date_field.SetValue(date_created)
        self.copyright_field.SetValue(copyright_notice)
        
        # Update character count and apply styling
        self.on_caption_text(None)
        
        logger.info("Updated UI from metadata manager")
    
    def update_manager_from_ui(self):
        """Update the metadata manager with values from the UI."""
        # Get values from UI
        headline = self.headline_field.GetValue()
        object_name = self.object_name_field.GetValue()
        caption = self.caption_field.GetValue()
        creator = self.creator_field.GetValue()
        creator_title = self.creator_title_field.GetValue()
        writer_editor = self.writer_editor_field.GetValue()
        credit = self.credit_field.GetValue()
        source = self.source_field.GetValue()
        date_created = self.date_field.GetValue()
        copyright_notice = self.copyright_field.GetValue()
        
        # Update metadata manager
        self.metadata_manager.set_field("Headline", headline)
        self.metadata_manager.set_field("ObjectName", object_name)
        self.metadata_manager.set_field("Caption-Abstract", caption)
        self.metadata_manager.set_field("By-line", creator)
        self.metadata_manager.set_field("By-lineTitle", creator_title)
        self.metadata_manager.set_field("Writer-Editor", writer_editor)
        self.metadata_manager.set_field("Credit", credit)
        self.metadata_manager.set_field("Source", source)
        self.metadata_manager.set_field("DateCreated", date_created)
        self.metadata_manager.set_field("Copyright", copyright_notice)
        
        logger.info("Updated metadata manager from UI")
    
    def clear_fields(self):
        """Clear all metadata fields."""
        self.headline_field.Clear()
        self.object_name_field.Clear()
        self.caption_field.Clear()
        self.creator_field.Clear()
        self.creator_title_field.Clear()
        self.writer_editor_field.Clear()
        self.credit_field.Clear()
        self.source_field.Clear()
        self.date_field.Clear()
        self.copyright_field.Clear()
        
        # Update character count and reset styling
        self._last_styled_length = 0
        self.on_caption_text(None)
        
        logger.info("Cleared all metadata fields")
    
    def set_today_date(self):
        """Set the date field to today's date in YYYY:MM:DD format."""
        today = datetime.datetime.now().strftime("%Y:%m:%d")
        self.date_field.SetValue(today)
        logger.info(f"Set date field to today: {today}")
    
    def on_write(self, event):
        """Handle Write Metadata button clicks."""
        # Update metadata manager from UI
        self.update_manager_from_ui()
        
        # Get parent frame to access selected file
        frame = wx.GetTopLevelParent(self)
        
        # Save metadata
        if hasattr(frame, "on_save"):
            frame.on_save(event)

    def refresh_layout(self):
        """
        Refresh the layout after zoom changes.
        This ensures proper sizing and positioning of all elements.
        """
        try:
            # Adjust scroll rate based on current zoom level
            if hasattr(self, 'scroll') and self.scroll and hasattr(self.GetTopLevelParent(), 'ui_zoom_factor'):
                try:
                    zoom = self.GetTopLevelParent().ui_zoom_factor
                    scroll_rate = int(20 * zoom)  # Scale scroll rate with zoom
                    self.scroll.SetScrollRate(0, scroll_rate)
                except Exception as e:
                    logger.error(f"Error adjusting scroll rate: {e}")
            
            # Ensure all nested elements update
            if hasattr(self, 'fields_panel') and self.fields_panel:
                try:
                    self.fields_panel.Layout()
                except Exception as e:
                    logger.error(f"Error updating fields panel layout: {e}")
                    
            # Force complete layout refresh - with safety checks
            if hasattr(self, 'scroll') and self.scroll:
                try:
                    self.scroll.FitInside()
                    self.scroll.Refresh()
                except Exception as e:
                    logger.error(f"Error refreshing scroll panel: {e}")
                    
            # Refresh the panel layout
            try:
                self.Layout()
                self.Refresh()
            except Exception as e:
                logger.error(f"Error refreshing panel layout: {e}")
                
        except Exception as e:
            logger.error(f"Error in refresh_layout: {e}")
