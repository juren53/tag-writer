"""
Tag Writer - WindowMixin: eventFilter, keyPressEvent, geometry save/restore, closeEvent.
"""

import logging

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt

from .config import config

logger = logging.getLogger(__name__)


class WindowMixin:
    """Mixin providing window event handling, geometry persistence, and close behavior."""

    def eventFilter(self, obj, event):
        """Application-level event filter to intercept arrow keys and Ctrl+mouse wheel."""
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                self.on_previous()
                return True
            elif event.key() == Qt.Key.Key_Down:
                self.on_next()
                return True
        elif event.type() == event.Type.Wheel:
            if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier:
                delta = event.angleDelta().y()
                if delta > 0:
                    self.zoom_ui(0.05)
                else:
                    self.zoom_ui(-0.05)
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        """Handle key press events for main window navigation."""
        if event.key() == Qt.Key.Key_Up:
            self.on_previous()
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.on_next()
            event.accept()
        elif event.key() == Qt.Key.Key_F5:
            self.on_refresh()
            event.accept()
        else:
            super().keyPressEvent(event)

    def save_window_geometry(self):
        """Save the current window geometry and state to config."""
        try:
            geometry = self.geometry()
            config.window_geometry = [geometry.x(), geometry.y(), geometry.width(), geometry.height()]
            config.window_maximized = self.isMaximized()
            config.save_config()
            logger.debug(f"Window geometry saved: {config.window_geometry}, maximized: {config.window_maximized}")
        except Exception as e:
            logger.error(f"Error saving window geometry: {e}")

    def restore_window_geometry(self):
        """Restore window geometry and state from config."""
        try:
            if config.window_geometry and len(config.window_geometry) == 4:
                x, y, width, height = config.window_geometry

                from PyQt6.QtGui import QGuiApplication
                screen_geometry = QGuiApplication.primaryScreen().geometry()

                x = max(0, min(x, screen_geometry.width() - width))
                y = max(0, min(y, screen_geometry.height() - height))

                width = max(600, width)
                height = max(400, height)

                self.setGeometry(x, y, width, height)

                if config.window_maximized:
                    self.showMaximized()

                logger.debug(f"Window geometry restored: {[x, y, width, height]}, maximized: {config.window_maximized}")
            else:
                logger.debug("No saved window geometry found, using default size")
        except Exception as e:
            logger.error(f"Error restoring window geometry: {e}")
            self.resize(1000, 600)

    def cleanup_resources(self):
        """Clean up resources before closing."""
        try:
            self.save_window_geometry()
            config.save_config()

            if hasattr(self, 'metadata_panel'):
                QApplication.instance().removeEventFilter(self)

            if hasattr(self, 'image_viewer'):
                self.image_viewer.clear()

            if hasattr(self, 'metadata_manager'):
                self.metadata_manager.clear()

            # Stop persistent ExifTool process
            from .exiftool_utils import get_persistent_exiftool
            get_persistent_exiftool().stop()

            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def closeEvent(self, event):
        """Handle close events to ensure proper shutdown."""
        if self._is_closing:
            event.accept()
            return

        self._is_closing = True

        try:
            self.cleanup_resources()
            event.accept()
            QApplication.instance().quit()

        except Exception as e:
            logger.error(f"Error during close event: {e}")
            event.accept()
            QApplication.instance().quit()
