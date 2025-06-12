#!/usr/bin/python3
"""
Main frame module for tag-writer application.

This module defines the main application window and coordinates
the various UI components.
"""

import os
import logging
import wx
import wx.adv

from tag_writer.utils.config import config
from tag_writer.models.metadata import MetadataManager
from tag_writer.utils.file_operations import get_image_files

logger = logging.getLogger(__name__)

# Define color constants for themes
LIGHT_THEME = {
    'bg_color': wx.Colour(238, 234, 224),          # #EEE9E0 - Soft cream background with warm beige tint
    'text_color': wx.Colour(80, 71, 65),           # #504741 - Soft dark brown text (gentler than black)
    'accent_color': wx.Colour(230, 225, 215),      # #E6E1D7 - Warm, very subtle beige for buttons
    'input_bg_color': wx.Colour(245, 242, 234),    # #F5F2EA - Warm cream for input fields
    'panel_color': wx.Colour(225, 220, 210)        # #E1DCD2 - Gentle tan for panels
}

DARK_THEME = {
    'bg_color': wx.Colour(51, 51, 51),             # #333333 - Dark gray background
    'text_color': wx.Colour(240, 240, 240),        # #F0F0F0 - Light gray text
    'accent_color': wx.Colour(85, 85, 85),         # #555555 - Medium gray accent
    'input_bg_color': wx.Colour(68, 68, 68),       # #444444 - Slightly lighter input fields
    'panel_color': wx.Colour(60, 60, 60)           # #3C3C3C - Slightly lighter panels
}

class MainFrame(wx.Frame):
    """
    Main application window for tag-writer.
    
    This class is responsible for:
    - Creating and managing the main UI layout
    - Coordinating actions between different UI components
    - Handling application-level events
    """
    
    def __init__(self, parent=None, title="Tag Writer"):
        """
        Initialize the main application window.
        
        Args:
            parent: Parent window (None for top-level)
            title: Window title
        """
        super().__init__(
            parent, 
            title=title, 
            size=(1400, 900),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # Initialize managers and components
        self.metadata_manager = MetadataManager()
        
        # Initialize UI zoom properties
        self.ui_zoom_factor = config.ui_zoom_factor
        self.ui_min_zoom = 0.8
        self.ui_max_zoom = 1.5
        self.ui_zoom_step = 0.1
        self.ui_zoom_label = None
        
        # Store theme setting but don't apply it yet
        self.dark_mode = config.dark_mode
        # Minimally initialize theme - don't actually apply it during startup
        # self.current_theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        
        # Setup UI components
        self.setup_ui()
        
        # Load saved configuration
        self.load_config()
        
        # Set icon
        self.set_icon()
        
        # Bind events
        self.bind_events()
        
        # Set up status bar
        self.statusbar = self.CreateStatusBar(3)  # Three sections
        self.statusbar.SetStatusWidths([200, -1, 200])  # Left, Center, Right
        self.statusbar.SetStatusText("Ready", 0)
        self.statusbar.SetStatusText("", 1)  # Middle section for file path
        self.statusbar.SetStatusText(f"Ver {config.app_version} (2025-05-31)", 2)
        
        logger.info("Main frame initialized")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Create main panel and sizer
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create menus
        self.setup_menu()
        
        # Create top toolbar
        self.setup_toolbar()
        
        # Create main content area
        self.setup_content_area()
        
        # Set up main layout
        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self.panel)
        
        # Center on screen
        self.Centre()
        
        logger.info("UI setup complete")
    
    def setup_menu(self):
        """Set up application menus."""
        # Create menu bar
        menu_bar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open an image file")
        
        # Create Recent Files submenu
        self.recent_menu = wx.Menu()
        file_menu.AppendSubMenu(self.recent_menu, "&Recent Files")
        
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save metadata to file")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")
        
        # Edit menu
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_CLEAR, "&Clear Fields\tCtrl+L", "Clear all metadata fields")
        edit_menu.AppendSeparator()
        
        # Add Export/Import JSON options
        export_id = wx.NewId()
        import_id = wx.NewId()
        edit_menu.Append(export_id, "&Export to JSON...", "Export metadata to JSON file")
        edit_menu.Append(import_id, "&Import from JSON...", "Import metadata from JSON file")
        
        # Set today's date option
        set_date_id = wx.NewId()
        edit_menu.AppendSeparator()
        edit_menu.Append(set_date_id, "Set &Today's Date", "Set date field to today's date")
        
        # View menu
        view_menu = wx.Menu()
        view_tags_id = wx.NewId()
        view_menu.Append(view_tags_id, "&View All Tags...", "View all metadata tags")
        
        # Add dark mode toggle
        toggle_dark_mode_id = wx.NewId()
        self.dark_mode_item = view_menu.AppendCheckItem(toggle_dark_mode_id, "&Toggle Dark Mode\tCtrl+D", "Switch between light and dark mode")
        self.dark_mode_item.Check(self.dark_mode)
        
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About", "About Tag Writer")
        help_menu.Append(wx.ID_HELP, "&Help", "View help information")
        
        license_id = wx.NewId()
        help_menu.Append(license_id, "&License", "View license information")
        
        # Add menus to menu bar
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(edit_menu, "&Edit")
        menu_bar.Append(view_menu, "&View")
        menu_bar.Append(help_menu, "&Help")
        
        # Set menu bar
        self.SetMenuBar(menu_bar)
        
        # Bind additional menu events
        self.Bind(wx.EVT_MENU, self.on_export_json, id=export_id)
        self.Bind(wx.EVT_MENU, self.on_import_json, id=import_id)
        self.Bind(wx.EVT_MENU, self.on_set_today_date, id=set_date_id)
        self.Bind(wx.EVT_MENU, self.on_view_all_tags, id=view_tags_id)
        self.Bind(wx.EVT_MENU, self.on_license, id=license_id)
        self.Bind(wx.EVT_MENU, self.on_toggle_dark_mode, id=toggle_dark_mode_id)
        
        logger.info("Menu setup complete")
    
    def setup_toolbar(self):
        """Set up the application toolbar."""
        toolbar_panel = wx.Panel(self.panel)
        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Create toolbar buttons
        self.btn_select_file = wx.Button(toolbar_panel, label="Select File")
        toolbar_sizer.Add(self.btn_select_file, 0, wx.ALL, 5)
        
        self.nav_prev_button = wx.Button(toolbar_panel, label="< Previous")
        toolbar_sizer.Add(self.nav_prev_button, 0, wx.ALL, 5)
        
        self.nav_next_button = wx.Button(toolbar_panel, label="Next >")
        toolbar_sizer.Add(self.nav_next_button, 0, wx.ALL, 5)
        
        # Add UI zoom controls
        zoom_panel = wx.Panel(toolbar_panel)
        zoom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Zoom out button
        zoom_out_btn = wx.Button(zoom_panel, label="-", size=(30, -1))
        zoom_out_btn.Bind(wx.EVT_BUTTON, lambda evt: self.zoom_ui(-self.ui_zoom_step))
        zoom_sizer.Add(zoom_out_btn, 0, wx.ALL, 5)
        
        # Zoom info label
        self.ui_zoom_label = wx.StaticText(zoom_panel, label="UI Zoom: 100%")
        zoom_sizer.Add(self.ui_zoom_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Zoom in button
        zoom_in_btn = wx.Button(zoom_panel, label="+", size=(30, -1))
        zoom_in_btn.Bind(wx.EVT_BUTTON, lambda evt: self.zoom_ui(self.ui_zoom_step))
        zoom_sizer.Add(zoom_in_btn, 0, wx.ALL, 5)
        
        # Reset zoom button
        reset_zoom_btn = wx.Button(zoom_panel, label="Reset", size=(50, -1))
        reset_zoom_btn.Bind(wx.EVT_BUTTON, lambda evt: self.reset_ui_zoom())
        zoom_sizer.Add(reset_zoom_btn, 0, wx.ALL, 5)
        
        zoom_panel.SetSizer(zoom_sizer)
        toolbar_sizer.Add(zoom_panel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Current file label
        self.file_label = wx.StaticText(toolbar_panel, label="No file selected")
        toolbar_sizer.Add(self.file_label, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        toolbar_panel.SetSizer(toolbar_sizer)
        self.main_sizer.Add(toolbar_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        logger.info("Toolbar setup complete")
    
    def setup_content_area(self):
        """Set up the main content area."""
        content_panel = wx.Panel(self.panel)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left side: Metadata editing panel
        # This will be created in a separate class
        from tag_writer.ui.metadata_panel import MetadataPanel
        self.metadata_panel = MetadataPanel(content_panel, self.metadata_manager)
        content_sizer.Add(self.metadata_panel, 1, wx.EXPAND | wx.RIGHT, 10)
        
        # Right side: Image preview panel
        # This will be created in a separate class
        from tag_writer.ui.image_viewer import ImageViewer
        self.image_viewer = ImageViewer(content_panel)
        content_sizer.Add(self.image_viewer, 1, wx.EXPAND | wx.ALL, 0)
        
        content_panel.SetSizer(content_sizer)
        self.main_sizer.Add(content_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        logger.info("Content area setup complete")
    
    def bind_events(self):
        """Bind event handlers to UI elements."""
        # Menu events
        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_clear, id=wx.ID_CLEAR)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_help, id=wx.ID_HELP)
        
        # Button events
        self.btn_select_file.Bind(wx.EVT_BUTTON, self.on_select_file)
        self.nav_prev_button.Bind(wx.EVT_BUTTON, self.on_previous)
        self.nav_next_button.Bind(wx.EVT_BUTTON, self.on_next)
        
        # Key events
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        
        # Bind keyboard shortcuts for zooming
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_for_zoom)
        
        # Don't apply any theme - disable all automatic theme application
        # wx.CallLater(500, self.safe_apply_theme)
        
        logger.info("Events bound")
    
    def set_icon(self):
        """Set the application icon."""
        try:
            # Look for icon in common locations
            icon_path = None
            for path in ["./resources/icon.png", "../resources/icon.png"]:
                if os.path.exists(path):
                    icon_path = path
                    break
            
            if icon_path:
                icon = wx.Icon(icon_path)
                self.SetIcon(icon)
                logger.info(f"Set application icon from {icon_path}")
            else:
                logger.warning("No icon file found")
        except Exception as e:
            logger.error(f"Error setting icon: {e}")
    
    def load_config(self):
        """Load saved configuration."""
        # Update recent files menu
        self.update_recent_files_menu()
        
        # Load last file if available
        if config.selected_file and os.path.exists(config.selected_file):
            self.load_file(config.selected_file)
        
        # Just store UI zoom factor, don't actually apply it yet
        self.ui_zoom_factor = config.ui_zoom_factor
        # Only update the label, don't apply actual zooming
        if self.ui_zoom_label:
            self.ui_zoom_label.SetLabel(f"UI Zoom: {int(self.ui_zoom_factor * 100)}%")
    
    def update_recent_files_menu(self):
        """Update the recent files menu with current items."""
        # Clear existing items
        while self.recent_menu.GetMenuItemCount() > 0:
            item = self.recent_menu.FindItemByPosition(0)
            self.recent_menu.Delete(item.GetId())
        
        # Add current items
        for i, file_path in enumerate(config.recent_files):
            if os.path.exists(file_path):
                # Create a shorthand name for display
                display_name = os.path.basename(file_path)
                if len(display_name) > 40:
                    display_name = display_name[:37] + "..."
                
                item_id = wx.ID_FILE1 + i
                self.recent_menu.Append(item_id, f"{i+1}: {display_name}")
                self.Bind(wx.EVT_MENU, lambda evt, path=file_path: self.load_file(path), id=item_id)
        
        # Add a separator and clear option if we have recent files
        if config.recent_files:
            self.recent_menu.AppendSeparator()
            clear_id = wx.NewId()
            self.recent_menu.Append(clear_id, "Clear Recent Files")
            self.Bind(wx.EVT_MENU, self.on_clear_recent, id=clear_id)
    
    def load_file(self, file_path):
        """
        Load a file and update UI components.
        
        Args:
            file_path: Path to the file to load
        """
        if not os.path.exists(file_path):
            wx.MessageBox(f"File not found: {file_path}", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        try:
            # Update the selected file
            config.selected_file = file_path
            config.add_recent_file(file_path)
            
            # Load directory files for navigation
            directory = os.path.dirname(file_path)
            config.directory_image_files = get_image_files(directory)
            
            # Find index of current file
            try:
                config.current_file_index = config.directory_image_files.index(file_path)
            except ValueError:
                config.current_file_index = -1
            
            # Load metadata
            self.metadata_manager.load_from_file(file_path)
            
            # Update UI components
            self.metadata_panel.update_from_manager()
            self.image_viewer.load_image(file_path)
            
            # Update window title
            self.SetTitle(f"Tag Writer - {os.path.basename(file_path)}")
            
            # Update status bar and file label
            self.statusbar.SetStatusText(f"Loaded {os.path.basename(file_path)}", 0)
            self.statusbar.SetStatusText(file_path, 1)
            self.file_label.SetLabel(os.path.basename(file_path))
            
            # Update recent files menu
            self.update_recent_files_menu()
            
            logger.info(f"Loaded file: {file_path}")
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            wx.MessageBox(f"Error loading file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    # Event handlers
    def on_open(self, event):
        """Handle File->Open menu event."""
        dialog = wx.FileDialog(
            self,
            message="Choose an image file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="Image files (*.jpg;*.jpeg;*.tif;*.tiff;*.png)|*.jpg;*.jpeg;*.tif;*.tiff;*.png",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            self.load_file(file_path)
        
        dialog.Destroy()
    
    def on_save(self, event):
        """Handle File->Save menu event."""
        if not config.selected_file:
            wx.MessageBox("No file selected", "Warning", wx.OK | wx.ICON_WARNING)
            return
        
        # Show a progress dialog
        progress = wx.ProgressDialog(
            "Writing Metadata",
            f"Writing metadata to {os.path.basename(config.selected_file)}...",
            maximum=100,
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
        )
        progress.Update(50)
        
        try:
            if self.metadata_manager.save_to_file(config.selected_file):
                progress.Update(100)
                wx.MessageBox("Metadata saved successfully", "Success", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("Error saving metadata", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            wx.MessageBox(f"Error saving metadata: {e}", "Error", wx.OK | wx.ICON_ERROR)
        finally:
            progress.Destroy()
    
    def on_exit(self, event):
        """Handle File->Exit menu event."""
        # Check for unsaved changes
        if self.metadata_manager.is_modified():
            dialog = wx.MessageDialog(
                self,
                "You have unsaved changes. Do you want to save before exiting?",
                "Unsaved Changes",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )
            
            result = dialog.ShowModal()
            dialog.Destroy()
            
            if result == wx.ID_CANCEL:
                return  # Don't exit
            elif result == wx.ID_YES:
                # Save changes
                if not self.metadata_manager.save_to_file(config.selected_file):
                    wx.MessageBox("Error saving metadata", "Error", wx.OK | wx.ICON_ERROR)
                    return  # Don't exit if save failed
        
        # Save UI zoom factor to config
        config.ui_zoom_factor = self.ui_zoom_factor
        
        # Save theme preference
        config.dark_mode = self.dark_mode
        
        # Save configuration
        config.save_config()
        
        # Close the application
        self.Destroy()
    
    def on_clear(self, event):
        """Handle Edit->Clear menu event."""
        self.metadata_panel.clear_fields()
        self.statusbar.SetStatusText("Metadata fields cleared", 0)
    
    def on_export_json(self, event):
        """Handle Edit->Export to JSON menu event."""
        if not config.selected_file:
            wx.MessageBox("No file selected", "Warning", wx.OK | wx.ICON_WARNING)
            return
        
        # Get suggested filename
        base_name = os.path.splitext(os.path.basename(config.selected_file))[0]
        suggested_path = os.path.join(os.path.dirname(config.selected_file), f"{base_name}_metadata.json")
        
        # Show file dialog
        dialog = wx.FileDialog(
            self,
            message="Export metadata to JSON file",
            defaultDir=os.path.dirname(suggested_path),
            defaultFile=os.path.basename(suggested_path),
            wildcard="JSON files (*.json)|*.json",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )
        
        if dialog.ShowModal() == wx.ID_OK:
            json_path = dialog.GetPath()
            
            try:
                # Update metadata from UI fields
                self.metadata_panel.update_manager_from_ui()
                
                # Export to JSON
                if self.metadata_manager.export_to_json(json_path):
                    wx.MessageBox(f"Metadata exported to {json_path}", "Export Successful", wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox("Error exporting metadata", "Export Error", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                logger.error(f"Error exporting metadata: {e}")
                wx.MessageBox(f"Error exporting metadata: {e}", "Export Error", wx.OK | wx.ICON_ERROR)
        
        dialog.Destroy()
    
    def on_import_json(self, event):
        """Handle Edit->Import from JSON menu event."""
        if not config.selected_file:
            wx.MessageBox("No file selected", "Warning", wx.OK | wx.ICON_WARNING)
            return
        
        # Show file dialog
        dialog = wx.FileDialog(
            self,
            message="Import metadata from JSON file",
            defaultDir=os.path.dirname(config.selected_file),
            defaultFile="",
            wildcard="JSON files (*.json)|*.json",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        if dialog.ShowModal() == wx.ID_OK:
            json_path = dialog.GetPath()
            
            try:
                # Import from JSON
                if self.metadata_manager.import_from_json(json_path):
                    # Update UI fields
                    self.metadata_panel.update_from_manager()
                    wx.MessageBox(f"Metadata imported from {json_path}", "Import Successful", wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox("Error importing metadata", "Import Error", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                logger.error(f"Error importing metadata: {e}")
                wx.MessageBox(f"Error importing metadata: {e}", "Import Error", wx.OK | wx.ICON_ERROR)
        
        dialog.Destroy()
    
    def on_set_today_date(self, event):
        """Handle Edit->Set Today's Date menu event."""
        self.metadata_panel.set_today_date()
    
    def on_view_all_tags(self, event):
        """Handle View->View All Tags menu event."""
        if not config.selected_file:
            wx.MessageBox("No file selected", "Warning", wx.OK | wx.ICON_WARNING)
            return
            
        # Get all metadata for the file
        from tag_writer.utils.file_operations import read_metadata
        try:
            all_metadata = read_metadata(config.selected_file)
            if all_metadata:
                # Show the metadata viewer dialog
                from tag_writer.ui.dialogs import TagListViewer
                viewer = TagListViewer(self, all_metadata)
                viewer.ShowModal()
                viewer.Destroy()
            else:
                wx.MessageBox("No metadata found in file", "No Metadata", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            logger.error(f"Error reading all metadata: {e}")
            wx.MessageBox(f"Error reading metadata: {e}", "Error", wx.OK | wx.ICON_ERROR)
    
    def on_about(self, event):
        """Handle Help->About menu event."""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Tag Writer")
        info.SetVersion(config.app_version)
        info.SetDescription("A tool for editing image metadata")
        info.SetCopyright("(c) 2023-2025")
        info.SetWebSite("https://example.com/tag-writer")
        info.AddDeveloper("Your Name")
        
        wx.adv.AboutBox(info)
    
    def on_help(self, event):
        """Handle Help->Help menu event."""
        help_text = (
            "Tag Writer Help\n\n"
            "This application allows you to view and edit IPTC metadata in image files.\n\n"
            "Basic Usage:\n"
            "1. Use File > Open to select an image file\n"
            "2. Edit metadata fields in the left panel\n"
            "3. Click 'Write Metadata' to save changes\n"
            "4. Use the navigation buttons or arrow keys to browse through images\n\n"
            "Keyboard Shortcuts:\n"
            "Ctrl+O - Open file\n"
            "Ctrl+S - Save metadata\n"
            "Ctrl+L - Clear all fields\n"
            "Left/Right Arrow - Navigate between images\n"
        )
        
        # Show help dialog
        dialog = wx.Dialog(self, title="Tag Writer Help", size=(500, 400))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.TextCtrl(dialog, value=help_text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(text, 1, wx.EXPAND | wx.ALL, 10)
        
        close_button = wx.Button(dialog, wx.ID_CLOSE, "Close")
        close_button.Bind(wx.EVT_BUTTON, lambda event: dialog.EndModal(wx.ID_CLOSE))
        sizer.Add(close_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        dialog.SetSizer(sizer)
        dialog.ShowModal()
        dialog.Destroy()
    
    def on_license(self, event):
        """Handle Help->License menu event."""
        license_text = (
            "MIT License\n\n"
            "Copyright (c) 2023-2025\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the \"Software\"), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all "
            "copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            "SOFTWARE."
        )
        
        # Show license dialog
        dialog = wx.Dialog(self, title="License Information", size=(500, 400))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.TextCtrl(dialog, value=license_text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(text, 1, wx.EXPAND | wx.ALL, 10)
        
        close_button = wx.Button(dialog, wx.ID_CLOSE, "Close")
        close_button.Bind(wx.EVT_BUTTON, lambda event: dialog.EndModal(wx.ID_CLOSE))
        sizer.Add(close_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        dialog.SetSizer(sizer)
        dialog.ShowModal()
        dialog.Destroy()
    
    def on_select_file(self, event):
        """Handle Select File button event."""
        self.on_open(event)
    
    def on_previous(self, event):
        """Handle Previous button event."""
        if not config.directory_image_files or config.current_file_index <= 0:
            return
        
        config.current_file_index -= 1
        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)
    
    def on_next(self, event):
        """Handle Next button event."""
        if not config.directory_image_files or config.current_file_index >= len(config.directory_image_files) - 1:
            return
        
        config.current_file_index += 1
        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)
    
    def on_clear_recent(self, event):
        """Handle Clear Recent Files menu event."""
        config.recent_files = []
        config.save_config()
        self.update_recent_files_menu()
    
    def on_key(self, event):
        """Handle keyboard events."""
        key_code = event.GetKeyCode()
        
        if key_code == wx.WXK_LEFT:
            self.on_previous(event)
        elif key_code == wx.WXK_RIGHT:
            self.on_next(event)
        else:
            event.Skip()
    
    def on_key_for_zoom(self, event):
        """Handle keyboard shortcuts for UI zoom."""
        # Check if Ctrl is pressed
        if event.ControlDown():
            key_code = event.GetKeyCode()
            
            # Ctrl+ for zoom in
            if key_code == ord('+') or key_code == wx.WXK_ADD:
                self.zoom_ui(self.ui_zoom_step)
                return  # Don't skip event
            
            # Ctrl- for zoom out
            elif key_code == ord('-') or key_code == wx.WXK_SUBTRACT:
                self.zoom_ui(-self.ui_zoom_step)
                return  # Don't skip event
            
            # Ctrl0 for reset zoom
            elif key_code == ord('0'):
                self.reset_ui_zoom()
                return  # Don't skip event
        
        # For other keys, pass the event up the chain
        event.Skip()
    
    def zoom_ui(self, zoom_delta):
        """Change the UI zoom level by the specified delta."""
        # Calculate new zoom level
        new_zoom = self.ui_zoom_factor + zoom_delta
        
        # Ensure zoom level is within bounds
        if self.ui_min_zoom <= new_zoom <= self.ui_max_zoom:
            self.ui_zoom_factor = new_zoom
            self.apply_ui_zoom()
            
            # Update zoom label
            if hasattr(self, 'ui_zoom_label') and self.ui_zoom_label:
                self.ui_zoom_label.SetLabel(f"UI Zoom: {int(self.ui_zoom_factor * 100)}%")
            
            # Update config
            config.ui_zoom_factor = self.ui_zoom_factor
    
    def reset_ui_zoom(self):
        """Reset UI zoom to 100%."""
        self.ui_zoom_factor = 1.0
        self.apply_ui_zoom()
        
        # Update zoom label
        if hasattr(self, 'ui_zoom_label') and self.ui_zoom_label:
            self.ui_zoom_label.SetLabel("UI Zoom: 100%")
        
        # Update config
        config.ui_zoom_factor = self.ui_zoom_factor
    
    def apply_ui_zoom(self):
        """Apply zoom level minimally."""
        try:
            # Just update the label for now
            if hasattr(self, 'ui_zoom_label') and self.ui_zoom_label:
                self.ui_zoom_label.SetLabel(f"UI Zoom: {int(self.ui_zoom_factor * 100)}%")
            logger.info(f"Set UI zoom to {int(self.ui_zoom_factor * 100)}%")
        except Exception as e:
            logger.error(f"Error updating zoom label: {e}")
    
    def scale_all_controls(self, parent):
        """Recursively scale all controls within a parent container."""
        try:
            # Safety check - ensure we have a valid parent with GetChildren method
            if not parent or not hasattr(parent, 'GetChildren') or not callable(parent.GetChildren):
                return
                
            for child in parent.GetChildren():
                try:
                    # Scale different control types
                    if isinstance(child, wx.TextCtrl) or isinstance(child, wx.richtext.RichTextCtrl):
                        self.scale_text_control(child)
                    elif isinstance(child, wx.StaticText):
                        self.scale_label_control(child)
                    elif isinstance(child, wx.Button):
                        self.scale_button_control(child)
                    
                    # If the child has children of its own, scale them too
                    if child and hasattr(child, 'GetChildren') and callable(child.GetChildren):
                        self.scale_all_controls(child)
                except Exception as e:
                    logger.error(f"Error scaling control: {e}")
                    continue  # Skip this control and continue with others
        except Exception as e:
            logger.error(f"Error in scale_all_controls: {e}")
    
    def scale_text_control(self, control):
        """Scale a text control font based on the current zoom factor."""
        if control and control.IsShown():
            # Get the current font
            current_font = control.GetFont()
            
            # Calculate the new size (base size is 9 points in most systems)
            base_size = 9
            new_size = int(base_size * self.ui_zoom_factor)
            
            # Create a new font with the scaled size
            new_font = wx.Font(
                new_size,
                current_font.GetFamily(),
                current_font.GetStyle(),
                current_font.GetWeight(),
                current_font.GetUnderlined()
            )
            
            # Apply the new font
            control.SetFont(new_font)
    
    def on_toggle_dark_mode(self, event):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        # Don't set current_theme - we're not applying it anyway
        # self.current_theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        
        # Update config
        config.dark_mode = self.dark_mode
        
        # Don't apply the theme, just update the status bar
        # self.apply_theme()
        
        # Update status bar
        theme_name = "dark" if self.dark_mode else "light"
        self.statusbar.SetStatusText(f"Switched to {theme_name} mode (theme not applied)", 0)
        logger.info(f"Theme preference set to {theme_name} (not applied to UI)")
    
    # Removed safe_apply_theme - not using it
    
    def apply_theme(self):
        """Minimal theme application that only updates status bar text."""
        theme_name = "dark" if self.dark_mode else "light"
        self.statusbar.SetStatusText(f"Using {theme_name} theme", 0)
        logger.info(f"Applied {theme_name} theme (minimal)")
    
    # Temporarily comment out the recursive theme application
    # def apply_theme_to_window(self, window):
    #     """Recursively apply theme to a window and all its children."""
    #     try:
    #         # Safety check for valid window
    #         if not window or not isinstance(window, wx.Window):
    #             return
    #             
    #         # Apply theme to the window itself
    #         if isinstance(window, wx.Frame) or isinstance(window, wx.Panel):
    #             try:
    #                 window.SetBackgroundColour(self.current_theme['bg_color'])
    #             except Exception as e:
    #                 logger.error(f"Error setting window background color: {e}")
    #         
    #         # Safety check for GetChildren method
    #         if not hasattr(window, 'GetChildren') or not callable(window.GetChildren):
    #             return
    #             
    #         # Apply to all children
    #         for child in window.GetChildren():
    #             try:
    #                 # Skip destroyed or invalid windows
    #                 if not child or not child.IsShown():
    #                     continue
    #                     
    #                 # Set background and foreground colors based on control type
    #                 if isinstance(child, wx.TextCtrl) or isinstance(child, wx.richtext.RichTextCtrl):
    #                     child.SetBackgroundColour(self.current_theme['input_bg_color'])
    #                     child.SetForegroundColour(self.current_theme['text_color'])
    #                 elif isinstance(child, wx.Button):
    #                     child.SetBackgroundColour(self.current_theme['accent_color'])
    #                     child.SetForegroundColour(self.current_theme['text_color'])
    #                 elif isinstance(child, wx.StaticText):
    #                     # For labels, make background transparent in light mode
    #                     if not self.dark_mode:
    #                         child.SetBackgroundColour(wx.NullColour)
    #                     else:
    #                         child.SetBackgroundColour(self.current_theme['bg_color'])
    #                     child.SetForegroundColour(self.current_theme['text_color'])
    #                 elif isinstance(child, wx.Panel):
    #                     child.SetBackgroundColour(self.current_theme['panel_color'])
    #                 
    #                 # Recursively apply to children if the child can have children
    #                 if hasattr(child, 'GetChildren') and callable(child.GetChildren):
    #                     self.apply_theme_to_window(child)
    #             except Exception as e:
    #                 logger.error(f"Error applying theme to control: {e}")
    #                 continue  # Skip this control and continue with others
    #     except Exception as e:
    #         logger.error(f"Error in apply_theme_to_window: {e}")
    
    def scale_label_control(self, control):
        """Scale a label control font based on the current zoom factor."""
        if control and control.IsShown():
            # Get the current font
            current_font = control.GetFont()
            
            # Calculate the new size (base size is 9 points in most systems)
            base_size = 9
            new_size = int(base_size * self.ui_zoom_factor)
            
            # Create a new font with the scaled size
            new_font = wx.Font(
                new_size,
                current_font.GetFamily(),
                current_font.GetStyle(),
                current_font.GetWeight(),
                current_font.GetUnderlined()
            )
            
            # Apply the new font
            control.SetFont(new_font)
    
    def scale_button_control(self, control):
        """Scale a button control font based on the current zoom factor."""
        if control and control.IsShown():
            # Get the current font
            current_font = control.GetFont()
            
            # Calculate the new size (base size is 9 points in most systems)
            base_size = 9
            new_size = int(base_size * self.ui_zoom_factor)
            
            # Create a new font with the scaled size
            new_font = wx.Font(
                new_size,
                current_font.GetFamily(),
                current_font.GetStyle(),
                current_font.GetWeight(),
                current_font.GetUnderlined()
            )
            
            # Apply the new font
            control.SetFont(new_font)
