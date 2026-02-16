"""
Tag Writer - ExifTool path resolution, persistent process, and timeout helper.
"""

import os
import sys
import subprocess
import logging
import concurrent.futures

import exiftool

from .constants import EXIFTOOL_TIMEOUT
from .platform import CREATE_NO_WINDOW, SW_HIDE

logger = logging.getLogger(__name__)

_exiftool_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def get_exiftool_path():
    """Resolve ExifTool path with 3-tier fallback.

    1. PyInstaller frozen: sys._MEIPASS / 'tools' / 'exiftool.exe'
    2. Development: <project>/tools/exiftool.exe
    3. Fallback: 'exiftool' (system PATH)
    """
    # Tier 1: PyInstaller frozen bundle
    if getattr(sys, 'frozen', False):
        bundled = os.path.join(sys._MEIPASS, 'tools', 'exiftool.exe')
        if os.path.exists(bundled):
            logger.info(f"ExifTool found in PyInstaller bundle: {bundled}")
            return bundled

    # Tier 2: Development - project tools/ directory
    # Walk up from this file to find the project root
    pkg_dir = os.path.dirname(os.path.abspath(__file__))  # src/tag_writer/
    project_root = os.path.normpath(os.path.join(pkg_dir, '..', '..'))  # tag-writer/
    dev_path = os.path.join(project_root, 'tools', 'exiftool.exe')
    if os.path.exists(dev_path):
        logger.info(f"ExifTool found in project tools: {dev_path}")
        return dev_path

    # Tier 3: System PATH fallback
    logger.info("ExifTool using system PATH fallback")
    return 'exiftool'


def execute_with_timeout(func, *args, timeout=EXIFTOOL_TIMEOUT):
    """Execute an ExifTool call with a timeout. Raises TimeoutError on timeout."""
    future = _exiftool_executor.submit(func, *args)
    return future.result(timeout=timeout)


def create_exiftool_instance(executable=None):
    """Create an ExifTool instance with Windows console window properly hidden."""
    if executable is None:
        executable = get_exiftool_path()

    if sys.platform.startswith('win'):
        class WindowsExifTool(exiftool.ExifTool):
            def run(self):
                """Override run method to hide console windows on Windows."""
                if self.running:
                    import warnings
                    warnings.warn("ExifTool already running; doing nothing.", UserWarning)
                    return

                proc_args = [self._executable]

                if hasattr(self, '_config_file') and self._config_file is not None:
                    proc_args.extend(["-config", self._config_file])

                proc_args.extend(["-stay_open", "True", "-@", "-"])

                if hasattr(self, '_common_args') and self._common_args:
                    proc_args.append("-common_args")
                    proc_args.extend(self._common_args)

                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = SW_HIDE

                try:
                    self._process = subprocess.Popen(
                        proc_args,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        startupinfo=startupinfo,
                        creationflags=CREATE_NO_WINDOW
                    )
                except Exception as e:
                    logger.error(f"Failed to create ExifTool process: {e}")
                    raise

                if self._process.poll() is not None:
                    self._process = None
                    raise RuntimeError("exiftool did not execute successfully")

                self._running = True

                try:
                    if hasattr(self, '_parse_ver'):
                        self._ver = self._parse_ver()
                    else:
                        self._ver = "unknown"
                except Exception:
                    self._ver = "unknown"

        return WindowsExifTool(executable=executable, encoding='utf-8')
    else:
        return exiftool.ExifTool(executable=executable, encoding='utf-8')


class PersistentExifTool:
    """Singleton persistent ExifTool process that stays alive for the app lifetime."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._et = None
        return cls._instance

    def start(self):
        """Start the persistent ExifTool process."""
        if self._et is not None and self._et.running:
            return
        try:
            self._et = create_exiftool_instance()
            self._et.__enter__()
            logger.info("Persistent ExifTool process started")
        except Exception as e:
            logger.error(f"Failed to start persistent ExifTool: {e}")
            self._et = None

    def stop(self):
        """Stop the persistent ExifTool process."""
        if self._et is not None:
            try:
                self._et.__exit__(None, None, None)
                logger.info("Persistent ExifTool process stopped")
            except Exception as e:
                logger.error(f"Error stopping persistent ExifTool: {e}")
            finally:
                self._et = None

    @property
    def et(self):
        """Get the ExifTool instance, starting it if needed."""
        if self._et is None or not self._et.running:
            self.start()
        return self._et

    def execute(self, *args):
        """Execute an ExifTool command via the persistent process."""
        return execute_with_timeout(self.et.execute, *args)

    def execute_json(self, *args):
        """Execute an ExifTool command returning JSON via the persistent process."""
        return execute_with_timeout(self.et.execute_json, *args)


# Module-level singleton
_persistent_et = PersistentExifTool()


def get_persistent_exiftool():
    """Get the persistent ExifTool singleton."""
    return _persistent_et


def check_exiftool_availability():
    """Check if ExifTool is available and accessible.

    Returns:
        tuple: (is_available, version_info, error_message)
    """
    try:
        et_instance = create_exiftool_instance()
        with et_instance as et:
            version_output = execute_with_timeout(et.execute, "-ver")
            version = version_output.strip() if version_output else "unknown"
            logger.info(f"ExifTool found - version: {version}")
            return True, version, None
    except FileNotFoundError:
        error_msg = "ExifTool executable not found. Please ensure ExifTool is installed and available in your system PATH."
        logger.error(error_msg)
        return False, None, error_msg
    except Exception as e:
        error_msg = f"ExifTool is installed but not accessible: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg


def show_exiftool_error_dialog(error_message):
    """Show an error dialog when ExifTool is not available."""
    from PyQt6.QtWidgets import QMessageBox

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("ExifTool Not Found")
    msg_box.setText("Tag Writer requires ExifTool to function properly.")
    msg_box.setDetailedText(f"Error: {error_message}\n\n"
                           "Please install ExifTool:\n"
                           "• Windows: Download from https://exiftool.org/ and add to PATH\n"
                           "• Linux: Install via package manager (e.g., 'sudo apt install exiftool')\n"
                           "• macOS: Install via Homebrew ('brew install exiftool')\n\n"
                           "After installation, restart Tag Writer.")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def show_exiftool_success_status(window, version):
    """Show ExifTool success status in the status bar."""
    from PyQt6.QtCore import QTimer

    def delayed_status_update():
        try:
            if hasattr(window, 'statusBar'):
                logger.info(f"Showing ExifTool status in status bar: ExifTool v{version} ready")
                window.statusBar.showMessage(f"ExifTool v{version} ready", 5000)
            else:
                logger.warning("Window does not have statusBar attribute")
        except Exception as e:
            logger.error(f"Error showing ExifTool status: {e}")

    QTimer.singleShot(100, delayed_status_update)
    logger.info(f"ExifTool v{version} is ready to use")
