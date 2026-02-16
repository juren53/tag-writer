"""
Tag Writer - FullImageViewer for viewing full-sized images with zoom and navigation.
"""

import os
import logging

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ..config import config
from ..image_utils import load_image, adjust_zoom, pil_to_pixmap

logger = logging.getLogger(__name__)


class FullImageViewer(QMainWindow):
    """Main window for viewing full-sized images with maximize/minimize controls."""

    def __init__(self, parent, image_path, pil_image):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Window |
                           Qt.WindowType.WindowMinimizeButtonHint |
                           Qt.WindowType.WindowMaximizeButtonHint |
                           Qt.WindowType.WindowCloseButtonHint)

        self.parent_window = parent
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

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        QTimer.singleShot(100, self.fit_to_window)

        self.update_navigation_buttons()

    def setup_ui(self):
        """Set up the user interface."""
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Scroll area with image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setScaledContents(False)

        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.on_mouse_press
        self.image_label.mouseMoveEvent = self.on_mouse_move
        self.image_label.mouseReleaseEvent = self.on_mouse_release
        self.image_label.wheelEvent = self.on_wheel

        self.image_label.installEventFilter(self)

        self.scroll_area.setWidget(self.image_label)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # Controls panel
        controls_widget = QWidget()
        controls_widget.setFixedWidth(100)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(5)
        controls_layout.setContentsMargins(5, 5, 5, 5)

        # Navigation buttons
        nav_group = QWidget()
        nav_layout = QVBoxLayout(nav_group)
        nav_layout.setSpacing(2)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        button_style = (
            "QPushButton {"
            "    padding: 8px;"
            "    letter-spacing: 1px;"
            "    background-color: #2b2b2b;"
            "    color: #ffffff;"
            "    border: 1px solid #555555;"
            "    border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #404040;"
            "    border-color: #666666;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #202020;"
            "    border-color: #888888;"
            "}"
        )

        self.nav_prev_btn = QPushButton("\u25b2  Previous")
        self.nav_prev_btn.setFixedWidth(120)
        self.nav_prev_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.nav_prev_btn.setStyleSheet(button_style)
        self.nav_prev_btn.clicked.connect(self.navigate_previous)
        nav_layout.addWidget(self.nav_prev_btn)

        self.nav_next_btn = QPushButton("Next  \u25bc")
        self.nav_next_btn.setFixedWidth(120)
        self.nav_next_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.nav_next_btn.setStyleSheet(button_style)
        self.nav_next_btn.clicked.connect(self.navigate_next)
        nav_layout.addWidget(self.nav_next_btn)

        controls_layout.addWidget(nav_group)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        controls_layout.addWidget(separator)

        # Zoom controls
        zoom_group = QWidget()
        zoom_layout = QVBoxLayout(zoom_group)
        zoom_layout.setSpacing(2)
        zoom_layout.setContentsMargins(0, 0, 0, 0)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(80)
        zoom_in_btn.clicked.connect(lambda: self.zoom(self.zoom_step))
        zoom_layout.addWidget(zoom_in_btn)

        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zoom_layout.addWidget(self.zoom_label)

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(80)
        zoom_out_btn.clicked.connect(lambda: self.zoom(-self.zoom_step))
        zoom_layout.addWidget(zoom_out_btn)

        controls_layout.addWidget(zoom_group)

        # Reset and Fit buttons
        buttons_group = QWidget()
        buttons_layout = QVBoxLayout(buttons_group)
        buttons_layout.setSpacing(2)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        reset_zoom_btn = QPushButton("Reset")
        reset_zoom_btn.setFixedWidth(80)
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        buttons_layout.addWidget(reset_zoom_btn)

        fit_btn = QPushButton("Fit")
        fit_btn.setFixedWidth(80)
        fit_btn.clicked.connect(self.fit_to_window)
        buttons_layout.addWidget(fit_btn)

        controls_layout.addWidget(buttons_group)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        controls_layout.addWidget(separator2)

        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        controls_layout.addWidget(self.info_label, 1)

        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        controls_layout.addWidget(separator3)

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.close)
        controls_layout.addWidget(close_btn)

        main_layout.addWidget(controls_widget, stretch=0)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def load_image(self):
        """Load and display the image."""
        if self.pil_image is None:
            return

        try:
            width, height = self.pil_image.size
            self.info_label.setText(f"Image Size: {width} x {height} pixels")
            self.status_bar.showMessage(f"Image: {os.path.basename(self.image_path)} - {width}x{height} pixels")
            self.update_display()
        except Exception as e:
            logger.error(f"Error loading full image: {e}")
            QMessageBox.warning(self, "Error", f"Error loading image: {str(e)}")

    def update_display(self):
        """Update the image display with the current zoom level."""
        try:
            zoomed_image = adjust_zoom(self.pil_image, self.zoom_factor)
            if zoomed_image is None:
                return

            pixmap = pil_to_pixmap(zoomed_image)
            if pixmap is None:
                return

            self.image_label.setPixmap(pixmap)
            self.image_label.setFixedSize(pixmap.size())

            zoom_percent = int(self.zoom_factor * 100)
            self.zoom_label.setText(f"Zoom: {zoom_percent}%")

            width, height = self.pil_image.size
            zoomed_width = int(width * self.zoom_factor)
            zoomed_height = int(height * self.zoom_factor)
            self.status_bar.showMessage(
                f"Image: {os.path.basename(self.image_path)} - "
                f"Original: {width}x{height} - "
                f"Zoomed: {zoomed_width}x{zoomed_height} - "
                f"Zoom: {zoom_percent}%"
            )
        except Exception as e:
            logger.error(f"Error updating image display: {e}")

    def zoom(self, delta):
        """Change zoom level by delta."""
        new_zoom = self.zoom_factor + delta
        if self.min_zoom <= new_zoom <= self.max_zoom:
            h_scroll_bar = self.scroll_area.horizontalScrollBar()
            v_scroll_bar = self.scroll_area.verticalScrollBar()

            h_ratio = h_scroll_bar.value() / max(1, h_scroll_bar.maximum())
            v_ratio = v_scroll_bar.value() / max(1, v_scroll_bar.maximum())

            self.zoom_factor = new_zoom
            self.update_display()

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

        img_width, img_height = self.pil_image.size

        viewport_size = self.scroll_area.viewport().size()
        viewport_width = viewport_size.width() - 20
        viewport_height = viewport_size.height() - 20

        viewport_width = max(viewport_width, 100)
        viewport_height = max(viewport_height, 100)

        width_scale = viewport_width / img_width
        height_scale = viewport_height / img_height

        self.zoom_factor = min(width_scale, height_scale)
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor))

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
        elif event.key() == Qt.Key.Key_Up:
            self.navigate_previous()
        elif event.key() == Qt.Key.Key_Down:
            self.navigate_next()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
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
            delta = event.position() - self.drag_position
            self.drag_position = event.position()

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
            self.zoom(self.zoom_step)
        elif delta < 0:
            self.zoom(-self.zoom_step)
        event.accept()

    def navigate_previous(self):
        """Navigate to the previous image in the directory."""
        main_window = None
        parent = self.parent_window
        while parent and not hasattr(parent, 'on_previous'):
            parent = parent.parent()

        if parent and hasattr(parent, 'on_previous'):
            main_window = parent

        if main_window:
            main_window.on_previous()
            if hasattr(config, 'selected_file') and config.selected_file:
                self.update_image_from_path(config.selected_file)
        else:
            self.navigate_using_config(-1)

    def navigate_next(self):
        """Navigate to the next image in the directory."""
        main_window = None
        parent = self.parent_window
        while parent and not hasattr(parent, 'on_next'):
            parent = parent.parent()

        if parent and hasattr(parent, 'on_next'):
            main_window = parent

        if main_window:
            main_window.on_next()
            if hasattr(config, 'selected_file') and config.selected_file:
                self.update_image_from_path(config.selected_file)
        else:
            self.navigate_using_config(1)

    def navigate_using_config(self, direction):
        """Fallback navigation using config directly with looping."""
        if not hasattr(config, 'directory_image_files') or not config.directory_image_files:
            return

        if not hasattr(config, 'current_file_index') or config.current_file_index < 0:
            return

        new_index = config.current_file_index + direction

        if new_index >= len(config.directory_image_files):
            new_index = 0
        elif new_index < 0:
            new_index = len(config.directory_image_files) - 1

        new_file = config.directory_image_files[new_index]
        config.current_file_index = new_index
        config.selected_file = new_file
        self.update_image_from_path(new_file)

    def update_image_from_path(self, image_path):
        """Update the full image viewer with a new image."""
        try:
            new_pil_image = load_image(image_path)
            if new_pil_image is None:
                logger.error(f"Failed to load new image: {image_path}")
                return

            self.image_path = image_path
            self.pil_image = new_pil_image

            self.fit_to_window()
            self.setWindowTitle(f"Full Image: {os.path.basename(image_path)}")
            self.update_navigation_buttons()

        except Exception as e:
            logger.error(f"Error updating image in full viewer: {e}")

    def update_navigation_buttons(self):
        """Update the state of navigation buttons based on current position."""
        if not hasattr(config, 'directory_image_files') or not config.directory_image_files:
            self.nav_prev_btn.setEnabled(False)
            self.nav_next_btn.setEnabled(False)
            return

        if not hasattr(config, 'current_file_index') or config.current_file_index < 0:
            self.nav_prev_btn.setEnabled(False)
            self.nav_next_btn.setEnabled(False)
            return

        has_images = len(config.directory_image_files) > 0
        self.nav_prev_btn.setEnabled(has_images)
        self.nav_next_btn.setEnabled(has_images)

        total_files = len(config.directory_image_files)
        current_pos = config.current_file_index + 1
        self.status_bar.showMessage(
            f"Image: {os.path.basename(self.image_path)} - "
            f"Image {current_pos} of {total_files} - "
            f"Original: {self.pil_image.size[0]}x{self.pil_image.size[1]} - "
            f"Zoom: {int(self.zoom_factor * 100)}%"
        )

    def eventFilter(self, obj, event):
        """Event filter to capture events from child widgets."""
        if obj is self.image_label and event.type() == event.Type.KeyPress:
            self.keyPressEvent(event)
            return True
        return super().eventFilter(obj, event)
