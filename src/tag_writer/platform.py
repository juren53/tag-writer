"""
Tag Writer - Platform-specific integrations (Windows taskbar, AppUserModelID).
"""

import os
import sys
import logging

from .constants import APP_USER_MODEL_ID

logger = logging.getLogger(__name__)

# Windows console window hiding constants
if sys.platform.startswith('win'):
    import ctypes
    from ctypes import wintypes
    CREATE_NO_WINDOW = 0x08000000
    SW_HIDE = 0
else:
    CREATE_NO_WINDOW = 0
    SW_HIDE = 0


def set_app_user_model_id():
    """Set Windows App User Model ID to distinguish this app from python.exe."""
    if sys.platform == 'win32':
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
            logger.info(f"Set Windows App User Model ID: {APP_USER_MODEL_ID}")
        except Exception as e:
            logger.warning(f"Could not set App User Model ID: {e}")


def set_windows_taskbar_icon(window_handle=None):
    """Set the taskbar icon on Windows using Windows API."""
    if not sys.platform.startswith('win'):
        return False

    try:
        import ctypes
        from ctypes import wintypes

        # Find icon file - check multiple locations
        possible_icon_dirs = [
            os.path.dirname(os.path.abspath(__file__)),  # Package dir
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'),  # Project root
            os.path.dirname(sys.argv[0]) if sys.argv[0] else '.',  # Script dir
        ]

        icon_path = None
        for d in possible_icon_dirs:
            candidate = os.path.join(d, "ICON_tw.ico")
            if os.path.exists(candidate):
                icon_path = os.path.abspath(candidate)
                break
            candidate = os.path.join(d, "ICON_tw.png")
            if os.path.exists(candidate):
                icon_path = os.path.abspath(candidate)
                break

        if not icon_path:
            return False

        # Set the application user model ID
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
        except:
            pass

        # If we have a window handle, set the icon directly
        if window_handle:
            try:
                if icon_path.endswith('.ico'):
                    icon_handle = ctypes.windll.user32.LoadImageW(
                        None, icon_path, 1, 0, 0, 0x00000010 | 0x00008000
                    )
                    if icon_handle:
                        ctypes.windll.user32.SendMessageW(
                            window_handle, 0x0080, 0, icon_handle  # WM_SETICON, ICON_SMALL
                        )
                        ctypes.windll.user32.SendMessageW(
                            window_handle, 0x0080, 1, icon_handle  # WM_SETICON, ICON_BIG
                        )
            except Exception as e:
                logger.error(f"Error setting window icon via API: {e}")

        return True

    except Exception as e:
        logger.error(f"Error setting Windows taskbar icon: {e}")
        return False
