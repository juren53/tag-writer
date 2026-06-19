"""
Tag Writer - Main application entry point.

MainWindow class composed from mixins + main() function.
"""

import os
import pathlib
import sys
import logging

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSplitter, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

# IMM setup at module level so _init_win32() fires before QApplication is created.
_IMM_PATH = os.path.expanduser("~/Projects/Icon_Manager_Module")
if os.path.isdir(_IMM_PATH) and _IMM_PATH not in sys.path:
    sys.path.insert(0, _IMM_PATH)

_app_icons = None
try:
    from icon_loader import IconLoader  # side-effect: _init_win32() on Windows
    _app_icons = IconLoader(
        base_path=pathlib.Path(__file__).resolve().parent.parent / "resources" / "icons"
    )
except Exception:
    pass

from tag_writer.constants import APP_NAME, APP_VERSION, APP_TIMESTAMP, APP_ORGANIZATION, APP_USER_MODEL_ID, IMAGE_EXTENSIONS
from tag_writer.config import config, SingleInstanceChecker
from tag_writer.exiftool_utils import check_exiftool_availability, show_exiftool_error_dialog, show_exiftool_success_status
from tag_writer.metadata import MetadataManager
from tag_writer.theme import DEFAULT_THEME, is_dark_theme
from tag_writer.widgets import MetadataPanel, ImageViewer
from tag_writer.menu import MenuMixin
from tag_writer.window import WindowMixin
from tag_writer.navigation import NavigationMixin
from tag_writer.file_ops import FileOpsMixin
from tag_writer.theme_mixin import ThemeMixin
from tag_writer.help import HelpMixin
from tag_writer.updates import UpdatesMixin

# Import version checker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from github_version_checker import GitHubVersionChecker

logger = logging.getLogger(__name__)


def get_app_icon() -> QIcon:
    if _app_icons is not None:
        return _app_icons.app_icon()
    return QIcon()


class MainWindow(MenuMixin, WindowMixin, NavigationMixin, FileOpsMixin,
                 ThemeMixin, HelpMixin, UpdatesMixin, QMainWindow):
    """Main application window composed from mixins."""

    def __init__(self):
        super().__init__()

        # Initialize managers
        self.metadata_manager = MetadataManager()

        # Initialize version checker
        self.version_checker = GitHubVersionChecker(
            repo_url="juren53/tag-writer",
            current_version=config.app_version,
            timeout=10
        )

        # Initialize state
        self.current_theme = config.current_theme
        self.dark_mode = is_dark_theme(self.current_theme)
        self.ui_scale_factor = config.ui_zoom_factor
        logger.debug(f"Loaded ui_scale_factor = {self.ui_scale_factor} from config")

        # Track if we're closing to prevent recursive close events
        self._is_closing = False

        # Ensure maximize button is present in the title bar
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # Set up UI
        self.setup_ui()

        # Install application-level event filter for arrow keys
        QApplication.instance().installEventFilter(self)

        # Apply saved theme
        self.apply_theme()

        # Apply saved UI zoom factor
        self.apply_ui_zoom()

        # Restore window geometry from saved config
        self.restore_window_geometry()

        # Check for updates on startup (if enabled)
        if config.auto_check_updates:
            QTimer.singleShot(3000, self.on_startup_update_check)

        logger.info("Main window initialized")

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Tag Writer")
        self.resize(1000, 600)

        self.setWindowIcon(get_app_icon())

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

        # Left/Middle section (stretches)
        path_container = QWidget()
        path_layout = QHBoxLayout(path_container)
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(5)

        # Path and status labels
        self.path_label = QLabel("")
        path_layout.addWidget(self.path_label)

        self.status_label = QLabel("Ready")
        path_layout.addWidget(self.status_label)

        # Add the container with stretch
        self.statusBar.addWidget(path_container, 1)

        # Right section - Version only
        version_label = QLabel(f"Ver {config.app_version} ({config.app_timestamp})")
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

        # Set up context menu for image viewer
        self.setup_image_context_menu()

    def setup_image_context_menu(self):
        """Set up context menu for the image viewer."""
        # The image viewer already has its context menu set up in its own class
        pass


def main():
    """Run the application."""
    # Check for single instance before creating QApplication
    instance_checker = SingleInstanceChecker("tag-writer")

    if instance_checker.is_already_running():
        logger.warning("Another instance of Tag Writer is already running")

        app = QApplication(sys.argv)
        QMessageBox.warning(
            None,
            "Tag Writer Already Running",
            "Another instance of Tag Writer is already running.\n\n"
            "Only one instance of Tag Writer can run at a time.\n"
            "Please use the existing instance or close it first.",
            QMessageBox.StandardButton.Ok
        )
        return 1

    logger.info("Single instance check passed - starting application")

    app = QApplication(sys.argv)

    # Set application name and organization
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setApplicationVersion(APP_VERSION)

    # Set application style
    app.setStyle("Fusion")

    # Set desktop filename for Linux icon integration
    app.setDesktopFileName("tag-writer")

    # Set application to quit when last window is closed
    app.setQuitOnLastWindowClosed(True)

    app.setWindowIcon(get_app_icon())

    # Handle command-line arguments for file paths
    file_to_open = None
    if len(sys.argv) > 1:
        potential_file = sys.argv[1]
        if os.path.exists(potential_file) and os.path.isfile(potential_file):
            file_ext = os.path.splitext(potential_file)[1].lower()
            if file_ext in IMAGE_EXTENSIONS:
                file_to_open = os.path.abspath(potential_file)
                logger.info(f"File to open from command line: {file_to_open}")

    # Check ExifTool availability before proceeding
    is_available, version, error_msg = check_exiftool_availability()

    # Create and show the main window
    window = MainWindow()
    window.show()

    if _app_icons is not None:
        _app_icons.set_taskbar_icon(window, APP_USER_MODEL_ID)

    # Show ExifTool status after window is visible
    if is_available:
        show_exiftool_success_status(window, version)
    else:
        show_exiftool_error_dialog(error_msg)

    # Load file from command line argument or last file if available
    if file_to_open:
        window.load_file(file_to_open)
    elif config.selected_file and os.path.exists(config.selected_file):
        window.load_file(config.selected_file)

    # Run the application
    try:
        exit_code = app.exec()
        instance_checker.release()
        return exit_code
    except KeyboardInterrupt:
        instance_checker.release()
        app.quit()
        return 0
    finally:
        instance_checker.release()


if __name__ == "__main__":
    sys.exit(main())
