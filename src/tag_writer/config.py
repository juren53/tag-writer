"""
Tag Writer - Configuration and single instance management.
"""

import os
import sys
import json
import logging
import tempfile

from .constants import APP_VERSION, APP_TIMESTAMP

logger = logging.getLogger(__name__)

# Platform-specific imports for file locking
if sys.platform.startswith('win'):
    import msvcrt
else:
    import fcntl


class SingleInstanceChecker:
    """
    Ensures only one instance of the application runs at a time.
    Uses file locking to prevent multiple instances.
    """
    def __init__(self, app_name="tag-writer"):
        self.app_name = app_name
        self.lock_file_path = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
        self.lock_file = None
        self.is_locked = False

    def is_already_running(self):
        """Check if another instance is already running."""
        try:
            self.lock_file = open(self.lock_file_path, 'w')

            if sys.platform.startswith('win'):
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    self.is_locked = True
                    self.lock_file.write(str(os.getpid()))
                    self.lock_file.flush()
                    return False
                except (OSError, IOError):
                    return True
            else:
                try:
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.is_locked = True
                    self.lock_file.write(str(os.getpid()))
                    self.lock_file.flush()
                    return False
                except (OSError, IOError):
                    return True
        except Exception as e:
            logger.error(f"Error checking for running instance: {e}")
            return False

    def release(self):
        """Release the lock file."""
        if self.is_locked and self.lock_file:
            try:
                if sys.platform.startswith('win'):
                    try:
                        msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    except:
                        pass
                else:
                    try:
                        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    except:
                        pass

                self.lock_file.close()
                self.is_locked = False

                try:
                    if os.path.exists(self.lock_file_path):
                        os.remove(self.lock_file_path)
                except:
                    pass
            except Exception as e:
                logger.error(f"Error releasing lock: {e}")

    def __del__(self):
        """Ensure lock is released when object is destroyed."""
        self.release()


class Config:
    """Global configuration and state management."""
    def __init__(self):
        self.app_version = APP_VERSION
        self.app_timestamp = APP_TIMESTAMP
        self.selected_file = None
        self.last_directory = None
        self.recent_files = []
        self.recent_directories = []
        self.directory_image_files = []
        self.current_file_index = -1
        self.dark_mode = False
        self.ui_zoom_factor = 1.0
        self.current_theme = 'Dark'
        self.window_geometry = None
        self.window_maximized = False

        # Version checking settings
        self.auto_check_updates = False
        self.last_update_check = None
        self.skipped_versions = []
        self.update_check_frequency = 86400  # 24 hours in seconds

        self.config_file = os.path.join(os.path.expanduser("~"), ".tag_writer_config.json")

        # Load configuration on startup
        self.load_config()

    def add_recent_file(self, file_path):
        """Add a file to the recent files list."""
        if file_path and os.path.exists(file_path):
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:5]
            self.save_config()

    def add_recent_directory(self, directory_path):
        """Add a directory to the recent directories list."""
        if directory_path and os.path.exists(directory_path) and os.path.isdir(directory_path):
            if directory_path in self.recent_directories:
                self.recent_directories.remove(directory_path)
            self.recent_directories.insert(0, directory_path)
            self.recent_directories = self.recent_directories[:5]
            self.save_config()

    def save_config(self):
        """Save configuration to file."""
        try:
            config_data = {
                'recent_files': self.recent_files,
                'recent_directories': self.recent_directories,
                'last_directory': self.last_directory,
                'dark_mode': self.dark_mode,
                'ui_zoom_factor': self.ui_zoom_factor,
                'current_theme': self.current_theme,
                'selected_file': self.selected_file,
                'window_geometry': self.window_geometry,
                'window_maximized': self.window_maximized,
                'auto_check_updates': self.auto_check_updates,
                'last_update_check': self.last_update_check,
                'skipped_versions': self.skipped_versions,
                'update_check_frequency': self.update_check_frequency
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f)
            logger.debug(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)

                self.recent_files = [f for f in config_data.get('recent_files', []) if os.path.exists(f)]
                self.recent_directories = [d for d in config_data.get('recent_directories', []) if os.path.exists(d) and os.path.isdir(d)]
                self.last_directory = config_data.get('last_directory', None)
                self.dark_mode = config_data.get('dark_mode', False)
                self.ui_zoom_factor = config_data.get('ui_zoom_factor', 1.0)
                self.current_theme = config_data.get('current_theme', 'Dark')
                self.selected_file = config_data.get('selected_file', None)
                self.window_geometry = config_data.get('window_geometry', None)
                self.window_maximized = config_data.get('window_maximized', False)

                self.auto_check_updates = config_data.get('auto_check_updates', False)
                self.last_update_check = config_data.get('last_update_check', None)
                self.skipped_versions = config_data.get('skipped_versions', [])
                self.update_check_frequency = config_data.get('update_check_frequency', 86400)

                logger.debug(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")


# Global configuration instance
config = Config()
