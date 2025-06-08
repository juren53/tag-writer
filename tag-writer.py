#!/usr/bin/env python3
"""
Tag Writer - PyQt6 Implementation with Integrated Core Functionality

This is an implementation of the Tag Writer application using PyQt6
that integrates the core metadata handling and image processing functionality
from the existing codebase.
"""
#-----------------------------------------------------------
# ############   tag-writer-wx.py  Ver 0.07a ################
# This program creates a GUI interface for entering and    
# writing IPTC metadata tags to TIF and JPG images selected   
# from a directory pick list using wxPython libraries.
# This program is intended as a free form metadata tagger
# when metada can not be pulled from an online database. 
#  Created Sat 01 Jul 2023 07:37:56 AM CDT   [IPTC]
#  Updated Sun 02 Jul 2023 04:53:41 PM CDT added no-backup	
#  Updated Sat 29 Mar 2025 07:51:49 PM CDT added read existing metadata from file for editing 
#  Updated Sun 30 Mar 2025 03:20:00 AM CDT added command-line argument support & status msg after write
#  Updated Tue 01 Apr 2025 08:55:00 AM CDT Ver .09 added export to JSON feature & clear data to Edit menu
#  Updated Wed 02 APr 2025 11:23:01 AM CSD Ver .10 added full image viewer from thumbnail & License window under Help
#
#  Updated Sat 05 Apr 2025 11:24:00 PM CDT Converted from tkinter to wxPython
#  Updated Sun 13 Apr 2025 10:20:00 AM CDT v 0.04c Load last image on startup
#  Updated Sun 13 Apr 2025 12:44:00 AM CDT v 0.04d Key board arrow keys scroll								 
#  Updated Sun 25 May 2025 12:44:00 AM CDT v 0.05a Key board arrow keys scroll through CWD
#  Updated Tue 27 May 2025 12:44:00 AM CDT v 0.05b
#  Updated Tue 27 May 2025 12:44:00 AM CDT v 0.05c 
#  Updated Wed 28 May 2025 12:44:00 AM CDT v 0.05d Caption Abstract increased to 1000 char
#  Updated Fri 30 May 2025 05:22:18 PM CDT v 0.06a Added View/List all tags menu item
#  Updated Fri 30 May 2025 05:22:18 PM CDT v 0.06b Fixed bug in the Caption Abstract text box editor

#  Updated Sat 31 May 2025 01:49:56 PM CDT v 0.07a Converted from wxPyton to PyQt6
#-----------------------------------------------------------

import os
import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QFormLayout, QScrollArea, QSplitter, QMenu, QMenuBar,
    QStatusBar, QFileDialog, QMessageBox, QToolBar, QDialog, QProgressDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QPalette, QColor, QPixmap, QImage

# Import from existing codebase
from tag_writer.models.metadata import MetadataManager
from tag_writer.utils.file_operations import get_image_files, backup_file
from tag_writer.utils.config import config

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Theme definitions - same as in the prototype
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
        
        # Convert to RGB if it's not already
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        
        # Convert to bytes
        byte_array = io.BytesIO()
        pil_image.save(byte_array, format='PNG')
        
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
        
        # Create metadata fields with mapping to model fields
        self.headline = QLineEdit()
        form.addRow("Headline:", self.headline)
        
        # Caption/Abstract with character count
        caption_container = QWidget()
        caption_layout = QVBoxLayout(caption_container)
        caption_layout.setContentsMargins(0, 0, 0, 0)
        caption_layout.setSpacing(2)
        
        self.caption = QTextEdit()
        self.caption.setMaximumHeight(100)
        caption_layout.addWidget(self.caption)
        
        # Character count label
        self.char_count_label = QLabel("0/1000 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setStyleSheet("font-size: 8pt;")
        caption_layout.addWidget(self.char_count_label)
        
        # Connect text changed signal to update character count
        self.caption.textChanged.connect(self.update_char_count)
        
        form.addRow("Caption/Abstract:", caption_container)
        
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
        self.write_button.clicked.connect(self.on_write_metadata)
        layout.addWidget(self.write_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
    def update_from_manager(self):
        """Update UI fields from metadata manager."""
        # Map field names to UI controls
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
            "Copyright": self.copyright
        }
        
        # Update each field
        for field_name, control in field_mappings.items():
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
            "Copyright": self.copyright.text()
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
        self.char_count_label.setText(f"{count}/1000 characters")
        
        # Apply visual feedback based on count
        if count > 1000:
            # Red for exceeding limit
            self.char_count_label.setStyleSheet("font-size: 8pt; color: red;")
            
            # Truncate text if over limit
            self.caption.blockSignals(True)  # Prevent recursive signal calls
            self.caption.setPlainText(text[:1000])
            self.caption.blockSignals(False)
            
            # Update count after truncation
            self.char_count_label.setText("1000/1000 characters")
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
        
        # Reset character count
        self.update_char_count()
        
    def set_today_date(self):
        """Set the date field to today's date."""
        today = datetime.now().strftime("%Y:%m:%d")
        self.date.setText(today)
        logger.info(f"Set date field to today: {today}")
    
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
        super().__init__(parent)
        self.current_image_path = None
        self.pil_image = None
        self.original_thumbnail = None
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
        self.view_button.clicked.connect(self.on_view_full_image)
        layout.addWidget(self.view_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Information container for filename, dimensions, and file size with minimal spacing
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)  # Zero spacing between labels for tight grouping
        
        # File name label
        self.filename_label = QLabel("File: --")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.filename_label)
        
        # Dimensions label
        self.dimensions_label = QLabel("Dimensions: --")
        self.dimensions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.dimensions_label)
        
        # File size label
        self.file_size_label = QLabel("File size: --")
        self.file_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.file_size_label)
        
        # Add the container to the main layout
        layout.addWidget(info_container)
        
    def load_image(self, image_path):
        """Load and display an image."""
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return False
            
        try:
            # Import here to prevent circular imports
            from tag_writer.utils.image_processing import load_image, create_thumbnail
            
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
            
            # Store path
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
            from tag_writer.utils.image_processing import create_thumbnail
            
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
        self.current_image_path = None
        self.pil_image = None
        self.original_thumbnail = None
    
    def on_view_full_image(self):
        """Handle View Full Image button click."""
        if not self.current_image_path or not self.pil_image:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return
            
        # Create and show full image viewer dialog
        viewer = FullImageViewer(self, self.current_image_path, self.pil_image)
        viewer.exec()

class FullImageViewer(QDialog):
    """Dialog for viewing full-sized images."""
    def __init__(self, parent, image_path, pil_image):
        super().__init__(parent)
        self.image_path = image_path
        self.pil_image = pil_image
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 0.1
        self.drag_position = None
        
        self.setup_ui()
        self.load_image()
        self.setWindowTitle(f"Full Image: {os.path.basename(self.image_path)}")
        
        # Set focus policy to accept keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def setup_ui(self):
        """Set up the user interface."""
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Image display in a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Image container
        self.image_container = QWidget()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        
        # Enable mouse tracking for dragging/panning
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.on_mouse_press
        self.image_label.mouseMoveEvent = self.on_mouse_move
        self.image_label.mouseReleaseEvent = self.on_mouse_release
        self.image_label.wheelEvent = self.on_wheel
        
        # Install event filter for keyboard events
        self.image_label.installEventFilter(self)
        
        container_layout = QVBoxLayout(self.image_container)
        container_layout.addWidget(self.image_label)
        container_layout.addStretch(1)
        
        self.scroll_area.setWidget(self.image_container)
        layout.addWidget(self.scroll_area)
        
        # Controls at the bottom
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Zoom controls
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(30)
        zoom_out_btn.clicked.connect(lambda: self.zoom(-self.zoom_step))
        controls_layout.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel("Zoom: 100%")
        controls_layout.addWidget(self.zoom_label)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(30)
        zoom_in_btn.clicked.connect(lambda: self.zoom(self.zoom_step))
        controls_layout.addWidget(zoom_in_btn)
        
        reset_zoom_btn = QPushButton("Reset Zoom")
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        controls_layout.addWidget(reset_zoom_btn)
        
        fit_btn = QPushButton("Fit to Window")
        fit_btn.clicked.connect(self.fit_to_window)
        controls_layout.addWidget(fit_btn)
        
        # Image info
        self.info_label = QLabel("")
        controls_layout.addWidget(self.info_label, 1)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        controls_layout.addWidget(close_btn)
        
        layout.addLayout(controls_layout)
        
        # Status bar for additional information
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
    
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
            from tag_writer.utils.image_processing import adjust_zoom
            
            # Apply zoom
            zoomed_image = adjust_zoom(self.pil_image, self.zoom_factor)
            if zoomed_image is None:
                return
                
            # Convert to pixmap and display
            pixmap = pil_to_pixmap(zoomed_image)
            if pixmap is None:
                return
                
            self.image_label.setPixmap(pixmap)
            
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
            
            # Adjust scroll area
            self.scroll_area.setWidgetResizable(False)
            self.image_label.adjustSize()
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
        viewport_width = self.scroll_area.width() - 20  # Account for scrollbar
        viewport_height = self.scroll_area.height() - 20
        
        # Calculate scale factors
        width_scale = viewport_width / img_width
        height_scale = viewport_height / img_height
        
        # Use the smaller scale to ensure the entire image fits
        self.zoom_factor = min(width_scale, height_scale)
        
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
        elif event.key() == Qt.Key.Key_Escape:
            self.accept()  # Close dialog
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
        font = QApplication.instance().font()
        font.setPointSizeF(9 * self.ui_scale_factor)  # Base size is 9pt
        
        # Apply to the application
        QApplication.instance().setFont(font)
        
        logger.info(f"Set UI zoom to {int(self.ui_scale_factor * 100)}%")
    
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

def main():
    """Run the application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Load last file if available
    if config.selected_file and os.path.exists(config.selected_file):
        window.load_file(config.selected_file)
    
    # Run the application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())

