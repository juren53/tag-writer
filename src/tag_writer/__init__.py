"""
Tag Writer - Modular image metadata editor.
"""

from .constants import APP_NAME, APP_VERSION, APP_TIMESTAMP
from .config import Config, SingleInstanceChecker, config
from .platform import set_app_user_model_id, set_windows_taskbar_icon
from .exiftool_utils import (
    get_exiftool_path, execute_with_timeout, create_exiftool_instance,
    PersistentExifTool, check_exiftool_availability,
    show_exiftool_error_dialog, show_exiftool_success_status
)
from .image_utils import load_image, create_thumbnail, adjust_zoom, pil_to_pixmap
from .file_utils import get_image_files, backup_file, read_metadata
from .metadata import MetadataManager
from .theme import ThemeManager, LIGHT_THEME, DARK_THEME

from .menu import MenuMixin
from .window import WindowMixin
from .navigation import NavigationMixin
from .file_ops import FileOpsMixin
from .theme_mixin import ThemeMixin
from .help import HelpMixin
from .updates import UpdatesMixin

from .widgets import MetadataPanel, ImageViewer, FullImageViewer
from .dialogs import ThemeDialog, PreferencesDialog

__all__ = [
    'APP_NAME', 'APP_VERSION', 'APP_TIMESTAMP',
    'Config', 'SingleInstanceChecker', 'config',
    'set_app_user_model_id', 'set_windows_taskbar_icon',
    'get_exiftool_path', 'execute_with_timeout', 'create_exiftool_instance',
    'PersistentExifTool', 'check_exiftool_availability',
    'show_exiftool_error_dialog', 'show_exiftool_success_status',
    'load_image', 'create_thumbnail', 'adjust_zoom', 'pil_to_pixmap',
    'get_image_files', 'backup_file', 'read_metadata',
    'MetadataManager', 'ThemeManager', 'LIGHT_THEME', 'DARK_THEME',
    'MenuMixin', 'WindowMixin', 'NavigationMixin', 'FileOpsMixin',
    'ThemeMixin', 'HelpMixin', 'UpdatesMixin',
    'MetadataPanel', 'ImageViewer', 'FullImageViewer',
    'ThemeDialog', 'PreferencesDialog',
]
