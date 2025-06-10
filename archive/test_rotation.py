#!/usr/bin/env python3
"""
Test script to verify that image rotation with FFmpeg preserves IPTC metadata
when using exiftool to copy metadata from the backup file.
"""

import os
import subprocess
import shutil
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
TEST_IMAGE = "./photos/test_rotation.jpg"
BACKUP_SUFFIX = "_backup_before_rotation"

def get_file_extension(filepath):
    """Get the file extension from a path."""
    _, ext = os.path.splitext(filepath)
    return ext

def extract_metadata(image_path):
    """Extract metadata from an image using exiftool and return as a dictionary."""
    try:
        cmd = ["exiftool", "-j", "-g", image_path]
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Parse the JSON output
        metadata = json.loads(result.stdout)
        return metadata[0] if metadata else {}
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting metadata: {e}")
        logger.error(f"Command output: {e.stderr}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing metadata JSON: {e}")
        return {}

def create_backup(image_path):
    """Create a backup of the image file."""
    file_name, file_ext = os.path.splitext(image_path)
    backup_path = f"{file_name}{BACKUP_SUFFIX}{file_ext}"
    
    logger.info(f"Creating backup: {backup_path}")
    shutil.copy2(image_path, backup_path)
    return backup_path

def rotate_with_ffmpeg(image_path, clockwise=True):
    """Rotate the image using FFmpeg."""
    # Determine rotation filter based on direction
    # transpose=1 = 90° clockwise, transpose=2 = 90° counterclockwise
    transpose_filter = "1" if clockwise else "2"
    
    # Get the file extension to use for the temporary file
    ext = get_file_extension(image_path)
    
    # Create a temporary filename with the correct extension
    temp_file = f"{image_path}_temp{ext}"
    
    try:
        cmd = [
            "ffmpeg", "-y", "-i", image_path,
            "-vf", f"transpose={transpose_filter}",
            "-map_metadata", "0",
            temp_file
        ]
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Replace the original file with the rotated one
        os.replace(temp_file, image_path)
        logger.info(f"Image rotated and saved to {image_path}")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error rotating image: {e}")
        logger.error(f"Command output: {e.stderr}")
        
        # Clean up the temp file if it exists
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def copy_metadata_with_exiftool(source_path, target_path):
    """Copy all metadata from source to target using exiftool."""
    try:
        cmd = [
            "exiftool", "-TagsFromFile", source_path,
            "-all:all", "-overwrite_original",
            target_path
        ]
        logger.info(f"Running exiftool command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Metadata copied: {result.stdout.strip()}")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error copying metadata: {e}")
        logger.error(f"Command output: {e.stderr}")
        return False

def compare_metadata(before, after):
    """Compare the metadata before and after rotation."""
    logger.info("Comparing metadata before and after rotation...")
    
    # Check if IPTC data exists in both
    iptc_before = before.get("IPTC", {})
    iptc_after = after.get("IPTC", {})
    
    if not iptc_before and not iptc_after:
        logger.warning("No IPTC metadata found in either image")
        return False
    
    # Check if any IPTC fields are missing after rotation
    missing_fields = []
    for key in iptc_before:
        if key not in iptc_after:
            missing_fields.append(key)
        elif iptc_before[key] != iptc_after[key]:
            logger.warning(f"IPTC field '{key}' changed: '{iptc_before[key]}' -> '{iptc_after[key]}'")
    
    if missing_fields:
        logger.error(f"Missing IPTC fields after rotation: {', '.join(missing_fields)}")
        return False
    
    # Check for any new fields (shouldn't happen but good to check)
    new_fields = []
    for key in iptc_after:
        if key not in iptc_before:
            new_fields.append(key)
    
    if new_fields:
        logger.warning(f"New IPTC fields after rotation: {', '.join(new_fields)}")
    
    logger.info("IPTC metadata successfully preserved!")
    return True

def main():
    """Main function to test rotation and metadata preservation."""
    if not os.path.exists(TEST_IMAGE):
        logger.error(f"Test image not found: {TEST_IMAGE}")
        return False
    
    # Create a test copy to work with
    test_file_name, test_file_ext = os.path.splitext(TEST_IMAGE)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_copy = f"{test_file_name}_{timestamp}{test_file_ext}"
    
    logger.info(f"Creating test copy: {test_copy}")
    shutil.copy2(TEST_IMAGE, test_copy)
    
    try:
        # Extract original metadata
        logger.info("Extracting original metadata...")
        original_metadata = extract_metadata(test_copy)
        
        # Create backup
        backup_path = create_backup(test_copy)
        
        # Rotate image
        logger.info("Rotating image clockwise...")
        if not rotate_with_ffmpeg(test_copy, clockwise=True):
            logger.error("Rotation failed!")
            return False
        
        # Extract metadata after rotation (before copying)
        logger.info("Extracting metadata after rotation (before copying from backup)...")
        after_rotation_metadata = extract_metadata(test_copy)
        
        # Copy metadata from backup to rotated image
        logger.info("Copying metadata from backup to rotated image...")
        if not copy_metadata_with_exiftool(backup_path, test_copy):
            logger.error("Metadata copying failed!")
            return False
        
        # Extract metadata after copying
        logger.info("Extracting metadata after copying from backup...")
        final_metadata = extract_metadata(test_copy)
        
        # Compare original and final metadata
        if compare_metadata(original_metadata, final_metadata):
            logger.info("TEST PASSED: Metadata was successfully preserved after rotation and metadata copying")
        else:
            logger.error("TEST FAILED: Metadata was not fully preserved")
        
        # Compare metadata after rotation but before copying
        logger.info("Checking if FFmpeg alone preserves metadata...")
        if compare_metadata(original_metadata, after_rotation_metadata):
            logger.info("FFmpeg alone successfully preserved the metadata (exiftool may not be needed)")
        else:
            logger.info("FFmpeg alone did not preserve metadata, confirming the need for exiftool")
    
    finally:
        # Clean up backup file
        if os.path.exists(backup_path):
            logger.info(f"Cleaning up: removing backup file {backup_path}")
            os.remove(backup_path)
        
        logger.info(f"Test complete. Test file kept for inspection: {test_copy}")

if __name__ == "__main__":
    main()

