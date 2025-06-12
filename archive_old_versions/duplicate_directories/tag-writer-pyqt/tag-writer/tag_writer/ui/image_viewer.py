#!/usr/bin/python3
"""
Image viewer module for tag-writer application.

This module provides UI components for displaying and interacting with images,
including a thumbnail viewer and a full-size image viewer with zoom capabilities.
"""

import os
import logging
import io
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QScrollArea,
    QHBoxLayout, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage

from tag_writer.utils.config import config

# Configure logging
logger = logging.getLogger(__name__)

def pil_to_pixmap(pil_image):
    """
    Convert PIL Image to QPixmap.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        QPixmap object or None if conversion fails
    """
    if pil_image is None:
        return None
        
    try:
        # Convert PIL Image to QImage
        from PIL import Image
        
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

class ImageViewer(QWidget):
    """
    Widget for displaying and interacting with images.
    
    This class provides a thumbnail view of an image along with a button
    to view the full-sized image.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the image viewer.
        
        Args:
            parent: Parent widget (default: None)
        """
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
        
        # Dimensions label
        self.dimensions_label = QLabel("Dimensions: --")
        self.dimensions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.dimensions_label)
        
    def load_image(self, image_path):
        """
        Load and display an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if successful, False otherwise
        """
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
            
            # Update dimensions label
            width, height = self.pil_image.size
            self.dimensions_label.setText(f"Dimensions: {width} x {height} pixels")
            
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
            QTimer.singleShot(100, self.update_thumbnail)
    
    def clear(self):
        """Clear the image display."""
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.dimensions_label.setText("Dimensions: --")
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
    """
    Dialog for viewing full-sized images.
    
    This class provides a scrollable view of a full-sized image with
    zoom and pan capabilities.
    """
    
    def __init__(self, parent, image_path, pil_image):
        """
        Initialize the full image viewer.
        
        Args:
            parent: Parent widget
            image_path: Path to the image file
            pil_image: PIL Image object
        """
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
        """
        Change zoom level by delta.
        
        Args:
            delta: Amount to change the zoom factor by
        """
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

#!/usr/bin/python3
"""
Image viewer module for tag-writer application.

This module provides UI components for displaying and interacting with images,
including a thumbnail viewer and a full-size image viewer with zoom capabilities.
"""

import os
import logging
import io
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QDialog, QScrollArea,
    QHBoxLayout, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage

from tag_writer.utils.config import config

# Configure logging
logger = logging.getLogger(__name__)

def pil_to_pixmap(pil_image):
    """
    Convert PIL Image to QPixmap.
    
    Args:
        pil_image: PIL Image object
        
    Returns:
        QPixmap object or None if conversion fails
    """
    if pil_image is None:
        return None
        
    try:
        # Convert PIL Image to QImage
        from PIL import Image
        
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

class ImageViewer(QWidget):
    """
    Widget for displaying and interacting with images.
    
    This class provides a thumbnail view of an image along with a button
    to view the full-sized image.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the image viewer.
        
        Args:
            parent: Parent widget (default: None)
        """
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
        
        # Dimensions label
        self.dimensions_label = QLabel("Dimensions: --")
        self.dimensions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.dimensions_label)
        
    def load_image(self, image_path):
        """
        Load and display an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if successful, False otherwise
        """
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
            
            # Update dimensions label
            width, height = self.pil_image.size
            self.dimensions_label.setText(f"Dimensions: {width} x {height} pixels")
            
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
            QTimer.singleShot(100, self.update_thumbnail)
    
    def clear(self):
        """Clear the image display."""
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.dimensions_label.setText("Dimensions: --")
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
    """
    Dialog for viewing full-sized images.
    
    This class provides a scrollable view of a full-sized image with
    zoom and pan capabilities.
    """
    
    def __init__(self, parent, image_path, pil_image):
        """
        Initialize the full image viewer.
        
        Args:
            parent: Parent widget
            image_path: Path to the image file
            pil_image: PIL Image object
        """
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
        """
        Change zoom level by delta.
        
        Args:
            delta: Amount to change the zoom factor by
        """
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

