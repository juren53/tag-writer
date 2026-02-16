"""
Tag Writer - Image processing utilities (PIL operations, QPixmap conversion).
"""

import io
import logging

from PyQt6.QtGui import QImage, QPixmap

logger = logging.getLogger(__name__)


def load_image(image_path):
    """Load an image using PIL with error handling."""
    try:
        from PIL import Image
        image = Image.open(image_path)

        # Handle orientation from EXIF data
        try:
            from PIL.ExifTags import ORIENTATION
            exif = image.getexif()
            if exif and ORIENTATION in exif:
                orientation = exif[ORIENTATION]

                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except Exception as e:
            logger.debug(f"Could not process EXIF orientation: {e}")

        # Convert 16-bit images to 8-bit for display
        if image.mode in ['I;16', 'I;16B']:
            import numpy as np
            np_image = np.array(image)
            ptp_value = np.ptp(np_image)
            if ptp_value > 0:
                norm_image = ((np_image - np_image.min()) / ptp_value * 255).astype(np.uint8)
            else:
                norm_image = np.zeros_like(np_image, dtype=np.uint8)
            image = Image.fromarray(norm_image, mode='L')

        return image
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None


def create_thumbnail(pil_image, max_size):
    """Create a thumbnail from a PIL image."""
    if pil_image is None:
        return None

    try:
        from PIL import Image
        thumbnail = pil_image.copy()

        if thumbnail.mode == 'I;16':
            thumbnail = thumbnail.convert('L')
        elif thumbnail.mode in ['I', 'F']:
            thumbnail = thumbnail.convert('RGB')

        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS

        thumbnail.thumbnail(max_size, resample_filter)
        return thumbnail
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None


def adjust_zoom(pil_image, zoom_factor):
    """Apply zoom factor to a PIL image."""
    if pil_image is None or zoom_factor <= 0:
        return None

    try:
        from PIL import Image
        original_width, original_height = pil_image.size
        new_width = int(original_width * zoom_factor)
        new_height = int(original_height * zoom_factor)

        if new_width <= 0 or new_height <= 0:
            return None

        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS

        resized = pil_image.resize((new_width, new_height), resample_filter)
        return resized
    except Exception as e:
        logger.error(f"Error adjusting zoom: {e}")
        return None


def pil_to_pixmap(pil_image):
    """Convert PIL Image to QPixmap."""
    if pil_image is None:
        return None

    try:
        from PIL import Image

        display_image = pil_image
        if pil_image.mode != 'RGB':
            display_image = pil_image.convert('RGB')

        byte_array = io.BytesIO()
        display_image.save(byte_array, format='PNG')

        byte_array.seek(0)
        qimg = QImage.fromData(byte_array.getvalue())

        pixmap = QPixmap.fromImage(qimg)
        return pixmap
    except Exception as e:
        logger.error(f"Error converting PIL image to QPixmap: {e}")
        return None
