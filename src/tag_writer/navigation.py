"""
Tag Writer - NavigationMixin: open, prev/next, load_file, recent files/dirs.
"""

import os
import logging

from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QApplication
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from .config import config
from .file_utils import get_image_files

logger = logging.getLogger(__name__)


class NavigationMixin:
    """Mixin providing file open, navigation, and recent files/directories."""

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

    def on_previous(self):
        """Navigate to the previous image in the directory with looping."""
        if not config.directory_image_files:
            self.status_label.setText("No images in directory")
            return

        if config.current_file_index <= 0:
            config.current_file_index = len(config.directory_image_files) - 1
            self.status_label.setText("Looped to last image")
        else:
            config.current_file_index -= 1
            self.status_label.setText("Previous image")

        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)

    def on_next(self):
        """Navigate to the next image in the directory with looping."""
        if not config.directory_image_files:
            self.status_label.setText("No images in directory")
            return

        if config.current_file_index >= len(config.directory_image_files) - 1:
            config.current_file_index = 0
            self.status_label.setText("Looped to first image")
        else:
            config.current_file_index += 1
            self.status_label.setText("Next image")

        file_path = config.directory_image_files[config.current_file_index]
        self.load_file(file_path)

    def load_file(self, file_path):
        """Load an image file and update the UI."""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file {file_path} does not exist.")
            return False

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        file_name = os.path.basename(file_path)
        self.status_label.setText(f"Loading {file_name}... Please wait")
        QApplication.processEvents()

        try:
            config.selected_file = file_path
            config.add_recent_file(file_path)

            directory = os.path.dirname(file_path)
            config.last_directory = directory
            config.directory_image_files = get_image_files(directory)

            config.add_recent_directory(directory)
            self.update_recent_directories_menu()

            try:
                config.current_file_index = config.directory_image_files.index(file_path)
            except ValueError:
                config.current_file_index = -1

            if not self.metadata_manager.load_from_file(file_path):
                self.metadata_panel.clear_fields()

            self.metadata_panel.update_from_manager()

            if not self.image_viewer.load_image(file_path):
                QMessageBox.warning(self, "Error", f"Failed to load image: {file_path}")
                return False

            self.file_label.setText(os.path.basename(file_path))
            self.path_label.setText(os.path.dirname(file_path))
            self.setWindowTitle(f"Tag Writer - {os.path.basename(file_path)}")
            self.status_label.setText(f"Loaded {os.path.basename(file_path)}")

            self.update_recent_menu()

            logger.info(f"Loaded file: {file_path}")
            return True

        finally:
            QApplication.restoreOverrideCursor()

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

    def update_recent_directories_menu(self):
        """Update the recent directories menu."""
        self.recent_directories_menu.clear()

        if not config.recent_directories:
            no_recent = QAction("No recent directories", self)
            no_recent.setEnabled(False)
            self.recent_directories_menu.addAction(no_recent)
            return

        for i, directory_path in enumerate(config.recent_directories):
            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                action = QAction(f"{i+1}: {directory_path}", self)
                action.triggered.connect(lambda checked=False, path=directory_path: self.open_directory(path))
                self.recent_directories_menu.addAction(action)

        self.recent_directories_menu.addSeparator()
        clear_action = QAction("Clear Recent Directories", self)
        clear_action.triggered.connect(self.on_clear_recent_directories)
        self.recent_directories_menu.addAction(clear_action)

    def on_clear_recent(self):
        """Clear the recent files list."""
        config.recent_files = []
        config.save_config()
        self.update_recent_menu()
        self.status_label.setText("Recent files cleared")

    def on_clear_recent_directories(self):
        """Clear the recent directories list."""
        config.recent_directories = []
        config.save_config()
        self.update_recent_directories_menu()
        self.status_label.setText("Recent directories cleared")

    def open_directory(self, directory_path):
        """Open a directory by finding the first image file and loading it."""
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            QMessageBox.warning(self, "Directory Not Found", f"The directory {directory_path} does not exist.")
            return

        image_files = get_image_files(directory_path)

        if not image_files:
            QMessageBox.information(self, "No Images", f"No image files found in directory {directory_path}")
            return

        first_image = image_files[0]
        self.load_file(first_image)

        config.add_recent_directory(directory_path)
        self.update_recent_directories_menu()

        self.status_label.setText(f"Opened directory: {os.path.basename(directory_path)}")
