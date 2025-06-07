#!/usr/bin/python3
"""
Image processing utilities for tag-writer application.

This module provides functions for loading, manipulating, and processing images,
including creating thumbnails and handling zoom operations.
"""

import os
import logging
from typing import Tuple, Optional
from PIL import Image, UnidentifiedImageError

# Configure logging
logger = logging.getLogger(__name__)

def load_image(image_path: str) -> Optional[Image.Image]:
    """
    Load an image file using PIL.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        PIL Image object or None if loading fails
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return None
        
    try:
        # Open the image with PIL
        image = Image.open(image_path)
        
        # Convert to RGB if needed for consistent handling
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
            
        return image
    except UnidentifiedImageError:
        logger.error(f"Cannot identify image file: {image_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None

def create_thumbnail(image: Image.Image, size: Tuple[int, int]) -> Optional[Image.Image]:
    """
    Create a thumbnail of the image at the specified size.
    
    Args:
        image: PIL Image object
        size: Tuple of (width, height) for the thumbnail
        
    Returns:
        Thumbnail as PIL Image object or None if creation fails
    """
    if image is None:
        logger.error("Cannot create thumbnail from None image")
        return None
        
    try:
        # Create a copy to avoid modifying the original
        thumbnail = image.copy()
        
        # Calculate the size that preserves aspect ratio
        width, height = image.size
        max_width, max_height = size
        
        # Calculate the scaling factor
        scale = min(max_width / width, max_height / height)
        
        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize the image using LANCZOS resampling for quality
        thumbnail = thumbnail.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return thumbnail
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None

def adjust_zoom(image: Image.Image, zoom_factor: float) -> Optional[Image.Image]:
    """
    Adjust the zoom level of an image.
    
    Args:
        image: PIL Image object
        zoom_factor: Factor to zoom by (1.0 = original size)
        
    Returns:
        Zoomed PIL Image object or None if operation fails
    """
    if image is None:
        logger.error("Cannot zoom None image")
        return None
        
    if zoom_factor <= 0:
        logger.error(f"Invalid zoom factor: {zoom_factor}")
        return None
        
    try:
        # Get original dimensions
        width, height = image.size
        
        # Calculate new dimensions
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)
        
        # Ensure minimum size
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        # Resize the image
        zoomed_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return zoomed_image
    except Exception as e:
        logger.error(f"Error adjusting zoom: {e}")
        return None

def rotate_image(image: Image.Image, degrees: float) -> Optional[Image.Image]:
    """
    Rotate an image by the specified degrees.
    
    Args:
        image: PIL Image object
        degrees: Degrees to rotate (positive = clockwise, negative = counter-clockwise)
        
    Returns:
        Rotated PIL Image object or None if operation fails
    """
    if image is None:
        logger.error("Cannot rotate None image")
        return None
        
    try:
        # Rotate the image
        # PIL's rotate is counter-clockwise, so negate the degrees
        rotated = image.rotate(-degrees, expand=True)
        
        return rotated
    except Exception as e:
        logger.error(f"Error rotating image: {e}")
        return None

def get_image_dimensions(image: Image.Image) -> Tuple[int, int]:
    """
    Get the dimensions of an image.
    
    Args:
        image: PIL Image object
        
    Returns:
        Tuple of (width, height)
    """
    if image is None:
        return (0, 0)
        
    return image.size

#!/usr/bin/python3
"""
Image processing utilities for tag-writer application.

This module provides functions for handling image operations such as:
- Loading and resizing images
- Creating thumbnails
- Converting between image formats
"""

import os
import logging
import io
from typing import Tuple, Optional, Any
from PIL import Image

logger = logging.getLogger(__name__)

def load_image(file_path: str) -> Optional[Image.Image]:
    """
    Load an image from a file path.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Loaded PIL Image object or None if loading fails
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    try:
        image = Image.open(file_path)
        logger.info(f"Successfully loaded image: {file_path}")
        return image
    except Exception as e:
        logger.error(f"Error loading image {file_path}: {e}")
        return None

def create_thumbnail(image: Image.Image, size: Tuple[int, int] = (200, 200)) -> Optional[Image.Image]:
    """
    Create a thumbnail from an image.
    
    Args:
        image: Source PIL Image object
        size: Thumbnail size as (width, height)
        
    Returns:
        Thumbnail image or None if creation fails
    """
    if image is None:
        logger.error("Cannot create thumbnail from None image")
        return None
    
    try:
        # Create a copy to avoid modifying the original
        thumbnail = image.copy()
        thumbnail.thumbnail(size)
        logger.info(f"Created thumbnail of size {thumbnail.size}")
        return thumbnail
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None

def resize_image(image: Image.Image, size: Tuple[int, int]) -> Optional[Image.Image]:
    """
    Resize an image to the specified dimensions.
    
    Args:
        image: Source PIL Image object
        size: Target size as (width, height)
        
    Returns:
        Resized image or None if resizing fails
    """
    if image is None:
        logger.error("Cannot resize None image")
        return None
    
    try:
        resized = image.resize(size, Image.LANCZOS)
        logger.info(f"Resized image to {size}")
        return resized
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return None

def pil_to_wx_image(pil_image: Image.Image) -> Any:
    """
    Convert a PIL Image to a wx.Image.
    
    Args:
        pil_image: Source PIL Image object
        
    Returns:
        wx.Image object
    
    Note:
        This function requires the wx module, which is imported here
        to avoid circular imports.
    """
    if pil_image is None:
        logger.error("Cannot convert None image to wx.Image")
        return None
    
    try:
        import wx
        
        # Convert PIL image to bytes
        image_bytes = io.BytesIO()
        pil_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        
        # Create wx.Image from bytes
        wx_image = wx.Image(image_bytes, type=wx.BITMAP_TYPE_PNG)
        logger.info(f"Converted PIL image to wx.Image of size {wx_image.GetWidth()}x{wx_image.GetHeight()}")
        return wx_image
    except Exception as e:
        logger.error(f"Error converting PIL image to wx.Image: {e}")
        return None

def adjust_zoom(image: Image.Image, factor: float) -> Optional[Image.Image]:
    """
    Adjust image zoom by a factor.
    
    Args:
        image: Source PIL Image object
        factor: Zoom factor (1.0 = original size, 2.0 = double size)
        
    Returns:
        Zoomed image or None if zooming fails
    """
    if image is None:
        logger.error("Cannot zoom None image")
        return None
    
    try:
        if factor <= 0:
            logger.warning(f"Invalid zoom factor {factor}, using 0.1")
            factor = 0.1
        
        new_width = int(image.width * factor)
        new_height = int(image.height * factor)
        
        zoomed = image.resize((new_width, new_height), Image.LANCZOS)
        logger.info(f"Zoomed image by factor {factor} to size {zoomed.size}")
        return zoomed
    except Exception as e:
        logger.error(f"Error zooming image: {e}")
        return None
