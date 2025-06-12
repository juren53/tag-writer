#!/usr/bin/python3
"""
Theme management module for tag-writer application.

Provides comprehensive theme support with multiple predefined themes,
theme selection dialog, and robust theme application system.
"""

import wx
import logging

logger = logging.getLogger(__name__)

class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        self.themes = {
            'Default Light': {
                'name': 'Default Light',
                'bg_color': wx.Colour(255, 255, 255),          # Pure white background
                'text_color': wx.Colour(0, 0, 0),              # Black text
                'accent_color': wx.Colour(240, 240, 240),      # Light gray for buttons
                'input_bg_color': wx.Colour(255, 255, 255),    # White input fields
                'panel_color': wx.Colour(248, 248, 248),       # Very light gray panels
                'border_color': wx.Colour(200, 200, 200),      # Medium gray borders
                'selection_bg': wx.Colour(51, 153, 255),       # Blue selection
                'selection_text': wx.Colour(255, 255, 255)     # White selection text
            },
            'Warm Light': {
                'name': 'Warm Light',
                'bg_color': wx.Colour(238, 234, 224),          # Soft cream background
                'text_color': wx.Colour(80, 71, 65),           # Soft dark brown text
                'accent_color': wx.Colour(230, 225, 215),      # Warm beige for buttons
                'input_bg_color': wx.Colour(245, 242, 234),    # Warm cream input fields
                'panel_color': wx.Colour(225, 220, 210),       # Gentle tan panels
                'border_color': wx.Colour(180, 170, 160),      # Warm gray borders
                'selection_bg': wx.Colour(102, 153, 204),      # Muted blue selection
                'selection_text': wx.Colour(255, 255, 255)     # White selection text
            },
            'Dark': {
                'name': 'Dark',
                'bg_color': wx.Colour(51, 51, 51),             # Dark gray background
                'text_color': wx.Colour(240, 240, 240),        # Light gray text
                'accent_color': wx.Colour(85, 85, 85),         # Medium gray accent
                'input_bg_color': wx.Colour(68, 68, 68),       # Slightly lighter input fields
                'panel_color': wx.Colour(60, 60, 60),          # Slightly lighter panels
                'border_color': wx.Colour(100, 100, 100),      # Medium gray borders
                'selection_bg': wx.Colour(74, 158, 255),       # Bright blue selection
                'selection_text': wx.Colour(255, 255, 255)     # White selection text
            },
            'Solarized Light': {
                'name': 'Solarized Light',
                'bg_color': wx.Colour(253, 246, 227),          # Solarized base3
                'text_color': wx.Colour(101, 123, 131),        # Solarized base00
                'accent_color': wx.Colour(238, 232, 213),      # Solarized base2
                'input_bg_color': wx.Colour(253, 246, 227),    # Solarized base3
                'panel_color': wx.Colour(245, 240, 231),       # Warmer base3
                'border_color': wx.Colour(211, 203, 183),      # Darker base2
                'selection_bg': wx.Colour(38, 139, 210),       # Solarized blue
                'selection_text': wx.Colour(253, 246, 227)     # Solarized base3
            },
            'Solarized Dark': {
                'name': 'Solarized Dark',
                'bg_color': wx.Colour(0, 43, 54),              # Solarized base03
                'text_color': wx.Colour(131, 148, 150),        # Solarized base0
                'accent_color': wx.Colour(7, 54, 66),          # Solarized base02
                'input_bg_color': wx.Colour(0, 43, 54),        # Solarized base03
                'panel_color': wx.Colour(10, 60, 73),          # Slightly lighter base03
                'border_color': wx.Colour(88, 110, 117),       # Solarized base01
                'selection_bg': wx.Colour(38, 139, 210),       # Solarized blue
                'selection_text': wx.Colour(0, 43, 54)         # Solarized base03
            },
            'High Contrast': {
                'name': 'High Contrast',
                'bg_color': wx.Colour(0, 0, 0),                # Pure black background
                'text_color': wx.Colour(255, 255, 255),        # Pure white text
                'accent_color': wx.Colour(51, 51, 51),         # Dark gray accent
                'input_bg_color': wx.Colour(0, 0, 0),          # Black input fields
                'panel_color': wx.Colour(20, 20, 20),          # Very dark gray panels
                'border_color': wx.Colour(255, 255, 255),      # White borders
                'selection_bg': wx.Colour(255, 255, 0),        # Yellow selection
                'selection_text': wx.Colour(0, 0, 0)           # Black selection text
            },
            'Monokai': {
                'name': 'Monokai',
                'bg_color': wx.Colour(39, 40, 34),             # Monokai background
                'text_color': wx.Colour(248, 248, 242),        # Monokai foreground
                'accent_color': wx.Colour(73, 72, 62),         # Monokai highlight
                'input_bg_color': wx.Colour(39, 40, 34),       # Monokai background
                'panel_color': wx.Colour(62, 61, 50),          # Darker highlight
                'border_color': wx.Colour(117, 113, 94),       # Monokai comment
                'selection_bg': wx.Colour(102, 217, 239),      # Monokai cyan
                'selection_text': wx.Colour(39, 40, 34)        # Monokai background
            }
        }
        self.current_theme_name = 'Default Light'
    
    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def get_theme(self, theme_name):
        """Get theme data by name"""
        return self.themes.get(theme_name, self.themes['Default Light'])
    
    def set_current_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            logger.info(f"Current theme set to: {theme_name}")
        else:
            logger.warning(f"Theme '{theme_name}' not found, using Default Light")
            self.current_theme_name = 'Default Light'
    
    def get_current_theme(self):
        """Get the current theme data"""
        return self.get_theme(self.current_theme_name)
    
    def is_dark_theme(self, theme_name=None):
        """Check if a theme is considered dark"""
        if theme_name is None:
            theme_name = self.current_theme_name
        
        theme = self.get_theme(theme_name)
        # Consider a theme dark if the background is darker than middle gray
        bg_color = theme['bg_color']
        brightness = (bg_color.Red() + bg_color.Green() + bg_color.Blue()) / 3
        return brightness < 128

class ThemeDialog(wx.Dialog):
    """Dialog for selecting application theme"""
    
    def __init__(self, parent, theme_manager, current_theme):
        super().__init__(parent, title="Select Theme", size=(450, 350))
        
        self.theme_manager = theme_manager
        self.selected_theme = current_theme
        
        self.setup_ui()
        self.Centre()
        
        logger.info("Theme selection dialog initialized")
    
    def setup_ui(self):
        """Set up the dialog user interface"""
        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Instructions
        instructions = wx.StaticText(self, label="Choose a theme for the application:")
        main_sizer.Add(instructions, 0, wx.ALL | wx.EXPAND, 10)
        
        # Theme selection
        theme_sizer = wx.BoxSizer(wx.HORIZONTAL)
        theme_label = wx.StaticText(self, label="Theme:")
        theme_sizer.Add(theme_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.theme_choice = wx.Choice(self, choices=self.theme_manager.get_theme_names())
        self.theme_choice.SetStringSelection(self.selected_theme)
        self.theme_choice.Bind(wx.EVT_CHOICE, self.on_theme_changed)
        theme_sizer.Add(self.theme_choice, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(theme_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Preview panel
        preview_box = wx.StaticBox(self, label="Preview")
        preview_sizer = wx.StaticBoxSizer(preview_box, wx.VERTICAL)
        
        self.preview_panel = wx.Panel(self, size=(400, 150))
        preview_content_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Preview text
        self.preview_text = wx.StaticText(self.preview_panel, 
            label="This is how text will appear with the selected theme.\n"
                  "You can see the background color, text color, and overall appearance.")
        preview_content_sizer.Add(self.preview_text, 0, wx.ALL, 10)
        
        # Preview button
        self.preview_button = wx.Button(self.preview_panel, label="Sample Button")
        preview_content_sizer.Add(self.preview_button, 0, wx.ALL, 10)
        
        # Preview text input
        self.preview_input = wx.TextCtrl(self.preview_panel, value="Sample text input field")
        preview_content_sizer.Add(self.preview_input, 0, wx.ALL | wx.EXPAND, 10)
        
        self.preview_panel.SetSizer(preview_content_sizer)
        preview_sizer.Add(self.preview_panel, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(preview_sizer, 1, wx.ALL | wx.EXPAND, 10)
        
        # Dialog buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        ok_button = wx.Button(self, wx.ID_OK, "OK")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        
        button_sizer.Add(ok_button, 0, wx.ALL, 5)
        button_sizer.Add(cancel_button, 0, wx.ALL, 5)
        
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        # Set sizer and update preview
        self.SetSizer(main_sizer)
        self.update_preview()
    
    def on_theme_changed(self, event):
        """Handle theme selection change"""
        self.selected_theme = self.theme_choice.GetStringSelection()
        self.update_preview()
        logger.info(f"Theme preview changed to: {self.selected_theme}")
    
    def update_preview(self):
        """Update the preview with selected theme colors"""
        theme = self.theme_manager.get_theme(self.selected_theme)
        
        # Apply theme to preview panel
        self.preview_panel.SetBackgroundColour(theme['bg_color'])
        self.preview_text.SetForegroundColour(theme['text_color'])
        self.preview_text.SetBackgroundColour(theme['bg_color'])
        
        # Apply theme to preview button
        self.preview_button.SetBackgroundColour(theme['accent_color'])
        self.preview_button.SetForegroundColour(theme['text_color'])
        
        # Apply theme to preview input
        self.preview_input.SetBackgroundColour(theme['input_bg_color'])
        self.preview_input.SetForegroundColour(theme['text_color'])
        
        # Refresh the preview panel
        self.preview_panel.Refresh()
        
    def get_selected_theme(self):
        """Get the selected theme name"""
        return self.selected_theme

