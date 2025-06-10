#!/usr/bin/env python3
"""
Tag Writer - PyQt6 Prototype

This is a prototype implementation of the Tag Writer application using PyQt6
instead of wxPython to demonstrate the benefits of the migration.
"""

import os
import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QFormLayout, QScrollArea, QSplitter, QMenu, QMenuBar,
    QStatusBar, QFileDialog, QMessageBox, QToolBar, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QPalette, QColor, QPixmap, QImage

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Application version
APP_VERSION = "0.06b"

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

class Config:
    """Simple configuration storage."""
    def __init__(self):
        self.dark_mode = False
        self.ui_scale_factor = 1.0
        self.recent_files = []
        self.selected_file = None
        
    def save(self):
        """Save configuration to file (placeholder)."""
        logger.info("Configuration saved")
        
    def load(self):
        """Load configuration from file (placeholder)."""
        logger.info("Configuration loaded")

class MetadataPanel(QWidget):
    """Panel for displaying and editing image metadata."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for metadata fields
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)
        
        # Create metadata fields
        self.headline = QLineEdit()
        form.addRow("Headline:", self.headline)
        
        self.caption = QTextEdit()
        self.caption.setMaximumHeight(100)
        form.addRow("Caption/Abstract:", self.caption)
        
        self.credit = QLineEdit()
        form.addRow("Credit:", self.credit)
        
        self.object_name = QLineEdit()
        form.addRow("Object Name:", self.object_name)
        
        self.writer = QLineEdit()
        form.addRow("Writer/Editor:", self.writer)
        
        self.byline = QLineEdit()
        form.addRow("By-line:", self.byline)
        
        self.byline_title = QLineEdit()
        form.addRow("By-line Title:", self.byline_title)
        
        self.source = QLineEdit()
        form.addRow("Source:", self.source)
        
        self.date = QLineEdit()
        form.addRow("Date Created:", self.date)
        
        self.copyright = QLineEdit()
        form.addRow("Copyright Notice:", self.copyright)
        
        # Wrap form in a scroll area for better handling of different screen sizes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_widget.setLayout(form)
        scroll.setWidget(form_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll)
        
        # Write metadata button
        self.write_button = QPushButton("Write Metadata")
        layout.addWidget(self.write_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
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
        
    def set_today_date(self):
        """Set the date field to today's date."""
        today = datetime.now().strftime("%Y:%m:%d")
        self.date.setText(today)
        logger.info(f"Set date field to today: {today}")

class ImageViewer(QWidget):
    """Widget for displaying and interacting with images."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Image display area
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        layout.addWidget(self.image_label)
        
        # View full image button
        self.view_button = QPushButton("View Full Image")
        layout.addWidget(self.view_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Dimensions label
        self.dimensions_label = QLabel("Dimensions: --")
        self.dimensions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.dimensions_label)
        
    def load_image(self, image_path):
        """Load and display an image."""
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return False
            
        try:
            # Load the image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                logger.error(f"Failed to load image: {image_path}")
                return False
                
            # Scale for thumbnail
            scaled_pixmap = pixmap.scaled(
                200, 200, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Display thumbnail
            self.image_label.setPixmap(scaled_pixmap)
            
            # Update dimensions label
            width = pixmap.width()
            height = pixmap.height()
            self.dimensions_label.setText(f"Dimensions: {width} x {height} pixels")
            
            # Store path
            self.current_image_path = image_path
            
            return True
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return False
            
    def clear(self):
        """Clear the image display."""
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.dimensions_label.setText("Dimensions: --")
        self.current_image_path = None

class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.config.load()
        
        # Initialize state
        self.dark_mode = self.config.dark_mode
        self.ui_scale_factor = self.config.ui_scale_factor
        
        # Set up UI
        self.setup_ui()
        
        # Apply theme
        self.apply_theme()
        
        logger.info("Main window initialized")
        
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
        self.statusBar.addPermanentWidget(QLabel("Ready"))
        
        # Middle section (stretches)
        self.path_label = QLabel("")
        self.statusBar.addWidget(self.path_label, 1)
        
        # Right section
        version_label = QLabel(f"Ver {APP_VERSION} (2025-05-31)")
        self.statusBar.addPermanentWidget(version_label)
        
        # Create splitter for metadata panel and image viewer
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Metadata panel (left side)
        self.metadata_panel = MetadataPanel()
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
        self.statusBar.showMessage(f"Applied {theme_name} theme", 3000)
        logger.info(f"Applied {theme_name} theme to UI")
    
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
            self.config.ui_scale_factor = self.ui_scale_factor
            self.config.save()
    
    def reset_zoom(self):
        """Reset UI zoom to 100%."""
        self.ui_scale_factor = 1.0
        self.apply_ui_zoom()
        self.zoom_label.setText("UI Zoom: 100%")
        self.config.ui_scale_factor = 1.0
        self.config.save()
    
    def apply_ui_zoom(self):
        """Apply the current zoom factor to all UI elements."""
        # Create a font with the current scale factor
        font = QApplication.instance().font()
        font.setPointSizeF(9 * self.ui_scale_factor)  # Base size is 9pt
        
        # Apply to the application
        QApplication.instance().setFont(font)
        
        logger.info(f"Set UI zoom to {int(self.ui_scale_factor * 100)}%")
    
    def on_open(self):
        """Handle Open action."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Image File",
            "",
            "Image Files (*.jpg *.jpeg *.tif *.tiff *.png)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def on_save(self):
        """Handle Save action."""
        if not self.config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        # Placeholder for actual save operation
        QMessageBox.information(self, "Metadata Saved", "Metadata has been saved successfully.")
        logger.info(f"Metadata saved to {self.config.selected_file}")
    
    def on_clear(self):
        """Handle Clear Fields action."""
        self.metadata_panel.clear_fields()
        self.statusBar.showMessage("All fields cleared", 3000)
    
    def on_export(self):
        """Handle Export to JSON action."""
        if not self.config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        # Show file dialog
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Export Metadata to JSON",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Placeholder for actual export operation
            QMessageBox.information(self, "Export Successful", f"Metadata exported to {file_path}")
            logger.info(f"Metadata exported to {file_path}")
    
    def on_import(self):
        """Handle Import from JSON action."""
        if not self.config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        # Show file dialog
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Import Metadata from JSON",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Placeholder for actual import operation
            QMessageBox.information(self, "Import Successful", f"Metadata imported from {file_path}")
            logger.info(f"Metadata imported from {file_path}")
    
    def on_set_today_date(self):
        """Handle Set Today's Date action."""
        self.metadata_panel.set_today_date()
    
    def on_view_all_tags(self):
        """Handle View All Tags action."""
        if not self.config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
            
        # Placeholder for actual implementation
        QMessageBox.information(self, "View All Tags", "This feature is not implemented in the prototype.")
    
    def on_toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        self.dark_mode_action.setChecked(self.dark_mode)
        self.apply_theme()
        
        # Update config
        self.config.dark_mode = self.dark_mode
        self.config.save()
    
    def on_previous(self):
        """Navigate to the previous image in the directory."""
        # Placeholder for actual implementation
        self.statusBar.showMessage("Previous image (not implemented in prototype)", 3000)
    
    def on_next(self):
        """Navigate to the next image in the directory."""
        # Placeholder for actual implementation
        self.statusBar.showMessage("Next image (not implemented in prototype)", 3000)
    
    def on_about(self):
        """Show About dialog."""
        QMessageBox.about(self,
            "About Tag Writer",
            f"Tag Writer version {APP_VERSION}\n\n"
            "A tool for editing image metadata\n\n"
            "© 2023-2025"
        )
    
    def on_help(self):
        """Show Help dialog."""
        QMessageBox.information(self,
            "Tag Writer Help",
            "This is a prototype of the Tag Writer application using PyQt6.\n\n"
            "The full implementation would include complete functionality for editing "
            "and saving IPTC metadata in image files."
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
    
    def load_file(self, file_path):
        """Load an image file and update the UI."""
        # Load image into viewer
        if self.image_viewer.load_image(file_path):
            # Update UI elements
            self.file_label.setText(os.path.basename(file_path))
            self.path_label.setText(file_path)
            self.setWindowTitle(f"Tag Writer - {os.path.basename(file_path)}")
            
            # Update config
            self.config.selected_file = file_path
            if file_path not in self.config.recent_files:
                self.config.recent_files.insert(0, file_path)
                if len(self.config.recent_files) > 5:
                    self.config.recent_files = self.config.recent_files[:5]
                self.config.save()
            
            self.statusBar.showMessage(f"Loaded {os.path.basename(file_path)}", 3000)
            logger.info(f"Loaded file: {file_path}")
            return True
        else:
            QMessageBox.warning(self, "Error", f"Failed to load image: {file_path}")
            return False

def main():
    """Run the application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())

