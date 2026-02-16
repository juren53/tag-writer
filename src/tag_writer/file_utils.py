"""
Tag Writer - File scanning, backup, and metadata reading utilities.
"""

import os
import logging

from .constants import IMAGE_EXTENSIONS
from .exiftool_utils import create_exiftool_instance, execute_with_timeout

logger = logging.getLogger(__name__)


def get_image_files(directory):
    """Get a sorted list of image files in the directory."""
    if not directory or not os.path.exists(directory):
        return []

    image_files = []

    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file(follow_symlinks=False):
                    _, ext = os.path.splitext(entry.name)
                    if ext.lower() in IMAGE_EXTENSIONS:
                        image_files.append(entry.path)

        image_files.sort(key=lambda x: os.path.basename(x).lower())
        return image_files
    except Exception as e:
        logger.error(f"Error getting image files from {directory}: {e}")
        return []


def backup_file(file_path):
    """Create a backup of the file with a unique name."""
    if not os.path.exists(file_path):
        return None

    backup_path = f"{file_path}_backup"
    counter = 1

    while os.path.exists(backup_path):
        backup_path = f"{file_path}_backup{counter}"
        counter += 1

    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None


def read_metadata(file_path):
    """Read all metadata from an image file."""
    if not os.path.exists(file_path):
        return {}

    try:
        et_instance = create_exiftool_instance()
        with et_instance as et:
            metadata_json = execute_with_timeout(et.execute_json, "-j", file_path)
            if metadata_json and len(metadata_json) > 0:
                return metadata_json[0]
            return {}
    except Exception as e:
        logger.error(f"Error reading metadata from {file_path}: {e}")
        return {}
