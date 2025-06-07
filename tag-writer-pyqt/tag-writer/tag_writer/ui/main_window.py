#!/usr/bin/python3
"""
Main window module for tag-writer application.

This module defines the main application window and coordinates
the various UI components.
"""

import os
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QSplitter, QMenu, QMenuBar,
    QStatusBar, QFileDialog, QMessageBox, QToolBar, QDialog, QProgressDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QPalette, QColor

from tag_writer.models.metadata import MetadataManager
from tag_writer.utils.config import config
from tag_writer.utils.file_operations import get_image_files, backup_file
from tag_writer.ui.metadata_panel import MetadataPanel
from tag_writer.ui.image_viewer import ImageViewer

# Configure logging
logger = logging.getLogger(__name__)

# Theme definitions
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

class MainWindow(QMainWindow):
    """
    Main application window for tag-writer.
    
    This class is responsible for:
    - Creating and managing the main UI layout
    - Coordinating actions between different UI components
    - Handling application-level events
    """
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        
        # Initialize managers
        self.metadata_manager = MetadataManager()
        
        # Initialize state
        self.dark_mode = config.dark_mode
        self.ui_scale_factor = config.ui_zoom_factor
        
        # Ensure maximize button is present in the title bar
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowMinimizeButtonHint | 
            Qt.WindowType.WindowMaximizeButtonHint | 
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Set up UI
        self.setup_ui()
        
        # Apply theme
        self.apply_theme()
        
        logger.info("Main window initialized")
        
    #
    # UI Setup Methods
    #
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Tag Writer")
        self.resize(1000, 600)
        
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
        
        # Left section
        self.status_label = QLabel("Ready")
        self.statusBar.addPermanentWidget(self.status_label)
        
        # Middle section (stretches)
        self.path_label = QLabel("")
        self.statusBar.addWidget(self.path_label, 1)
        
        # Right section
        version_label = QLabel(f"Ver {config.app_version} (2025-05-31)")
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
        
        date_action = QAction("Set &Today's Date", self)
        date_action.triggered.connect(self.on_set_today_date)
        edit_menu.addAction(date_action)
        
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
        
        tags_action = QAction("&View All Tags...", self)
        tags_action.triggered.connect(self.on_view_all_tags)
        view_menu.addAction(tags_action)
        
        view_menu.addSeparator()
        
        # Dark mode toggle
        self.dark_mode_action = QAction("&Toggle Dark Mode", self)
        self.dark_mode_action.setShortcut("Ctrl+D")
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.dark_mode_action.triggered.connect(self.on_toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
        help_action = QAction("&Help", self)
        help_action.triggered.connect(self.on_help)
        help_menu.addAction(help_action)
        
        license_action = QAction("&License", self)
        license_action.triggered.connect(self.on_license)
        help_menu.addAction(license_action)
        
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
        prev_btn = QPushButton("< Previous")
        prev_btn.clicked.connect(self.on_previous)
        toolbar.addWidget(prev_btn)
        
        next_btn = QPushButton("Next >")
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
    
    #
    # Theme Management Methods
    #
    
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
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().setPalette(palette)
        
        # Update status bar
        theme_name = "dark" if self.dark_mode else "light"
        self.status_label.setText(f"Applied {theme_name} theme")
        logger.info(f"Applied {theme_name} theme to UI")
    
    #
    # UI Zoom Methods
    #
    
    def zoom_ui(self, zoom_delta):
        """Change the UI zoom level by the specified delta."""
        # Calculate new zoom level
        new_zoom = self.ui_scale_factor + zoom_delta
        
        # Ensure zoom level is within bounds
        if 0.8 <= new_zoom <= 1.5:
            self.ui_scale_factor = new_zoom
            self.apply_ui_zoom()
            
            # Update zoom label
            self.zoom_label.setText(f"UI Zoom: {int(self.ui_scale_factor * 100)}%")
            
            # Update config
            config.ui_zoom_factor = self.ui_scale_factor
            config.save_config()
    
    def reset_zoom(self):
        """Reset UI zoom to 100%."""
        self.ui_scale_factor = 1.0
        self.apply_ui_zoom()
        self.zoom_label.setText("UI Zoom: 100%")
        config.ui_zoom_factor = 1.0
        config.save_config()
    
    def apply_ui_zoom(self):
        """Apply the current zoom factor to all UI elements."""
        # Create a font with the current scale factor
        font = QFont()
        font.setPointSizeF(9 * self.ui_scale_factor)  # Base size is 9pt
        
        # Apply to the application
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().setFont(font)
        
        logger.info(f"Set UI zoom to {int(self.ui_scale_factor * 100)}%")
    
    #
    # Menu Management Methods
    #
    
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
    
    #
    # Event Handler Methods
    #
    
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
    
    def on_view_all_tags(self):
        """Handle View All Tags action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        from tag_writer.utils.file_operations import read_metadata
        metadata = read_metadata(config.selected_file)
        
        if not metadata:
            QMessageBox.information(self, "No Metadata", "No metadata found in the selected file.")
            return
        
        # Display metadata in a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"All Tags: {os.path.basename(config.selected_file)}")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Create table with metadata
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Tag", "Value"])
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Fill table with metadata
        table.setRowCount(len(metadata))
        for i, (key, value) in enumerate(sorted(metadata.items())):
            table.setItem(i, 0, QTableWidgetItem(key))
            table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        layout.addWidget(table)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()
    
    def on_toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        self.dark_mode_action.setChecked(self.dark_mode)
        self.apply_theme()
        
        # Update config
        config.dark_mode = self.dark_mode
        config.save_config()
    
    def on_previous(self):
        """Navigate to the previous image in the directory."""
        if not config.directory_image_files or config.current_file_index <= 0:
            self.status_label.setText("Already at first image")
            return
        
        config.current_file_index -= 1
        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)
    
    def on_next(self):
        """Navigate to the next image in the directory."""
        if not config.directory_image_files or config.current_file_index >= len(config.directory_image_files) - 1:
            self.status_label.setText("Already at last image")
            return
        
        config.current_file_index += 1
        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)
    
    def on_clear_recent(self):
        """Clear the recent files list."""
        config.recent_files = []
        config.save_config()
        self.update_recent_menu()
        self.status_label.setText("Recent files cleared")
    
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
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt
        
        progress_dialog = QProgressDialog(
            f"Rotating image {abs(degrees)}° {'clockwise' if degrees > 0 else 'counter-clockwise'}...",
            "Cancel", 0, 100, self
        )
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(10)
        from PyQt6.QtWidgets import QApplication
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
            "© 2023-2025"
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
    
    def on_license(self):
        """Show License dialog."""
        QMessageBox.information(self,
            "License Information",
            "MIT License\n\n"
            "Copyright (c) 2023-2025\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files..."
        )
    
    #
    # File Handling Methods
    #
    
    def load_file(self, file_path):
        """
        Load an image file and update the UI.
        
        Args:
            file_path: Path to the image file to load
            
        Returns:
            True if successful, False otherwise
        """
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
        self.path_label.setText(file_path)
        self.setWindowTitle(f"Tag Writer - {os.path.basename(file_path)}")
        self.status_label.setText(f"Loaded {os.path.basename(file_path)}")
        
        # Update recent files menu
        self.update_recent_menu()
        
        logger.info(f"Loaded file: {file_path}")
        return True

