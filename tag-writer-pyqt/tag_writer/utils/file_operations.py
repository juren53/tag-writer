#!/usr/bin/python3
"""
File operation utilities for tag-writer application.

This module provides functions for handling file operations such as:
- Finding image files in directories
- Reading and writing metadata
- File validation and processing
"""

import os
import logging
import json
import shutil
import subprocess
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

def get_image_files(directory: str) -> List[str]:
    """
    Get a list of image files from a directory.
    
    Args:
        directory: Path to the directory to scan
        
    Returns:
        List of full paths to image files in the directory
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        logger.error(f"Invalid directory: {directory}")
        return []
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tif', '.tiff', '.png')
    
    image_files = []
    try:
        for file in os.listdir(directory):
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(directory, file)
                if os.path.isfile(full_path):
                    image_files.append(full_path)
        
        logger.info(f"Found {len(image_files)} image files in {directory}")
        return sorted(image_files)
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {e}")
        return []

def read_metadata(file_path: str) -> Dict[str, Any]:
    """
    Read metadata from an image file using exiftool.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Dictionary of metadata tags from the file
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {}
    
    try:
        # Run exiftool to read the metadata in JSON format
        cmd = ["exiftool", "-j", file_path]
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"Exiftool error: {result.stderr}")
            return {}
        
        # Parse the JSON output
        metadata_list = json.loads(result.stdout)
        if not metadata_list or not isinstance(metadata_list, list) or len(metadata_list) == 0:
            logger.warning(f"No metadata found in {file_path}")
            return {}
        
        # Process the metadata
        raw_metadata = metadata_list[0]  # Exiftool returns a list with one item per file
        
        # Ensure we have all the fields we need
        metadata = {}
        
        # Add standardized field names from raw_metadata
        field_mapping = {
            # IPTC Core fields
            "Headline": ["Headline"],
            "Caption-Abstract": ["Caption-Abstract", "Description"],
            "Credit": ["Credit"],
            "ObjectName": ["ObjectName", "Object Name"],
            "Writer-Editor": ["Writer-Editor"],
            "By-line": ["By-line", "Creator", "Author"],
            "By-lineTitle": ["By-lineTitle", "By-line Title"],
            "Source": ["Source"],
            "DateCreated": ["DateCreated", "Date Created"],
            "Copyright": ["Copyright", "CopyrightNotice", "Copyright Notice"],
        }
        
        # Extract fields using the mapping
        for target_field, source_fields in field_mapping.items():
            for source_field in source_fields:
                if source_field in raw_metadata:
                    metadata[target_field] = raw_metadata[source_field]
                    break
        
        logger.info(f"Successfully read metadata from {file_path}")
        return raw_metadata  # Return the full metadata for completeness
    except Exception as e:
        logger.error(f"Error reading metadata from {file_path}: {e}")
        return {}

def write_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
    """
    Write metadata to an image file using exiftool.
    
    Args:
        file_path: Path to the image file
        metadata: Dictionary of metadata tags to write
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        # Prepare exiftool arguments
        args = ["exiftool"]
        
        # Add metadata fields
        for tag, value in metadata.items():
            if value:  # Only include non-empty values
                args.append(f"-{tag}={value}")
        
        # Add overwrite original flag
        args.append("-overwrite_original")
        
        # Add file path
        args.append(file_path)
        
        # Run exiftool
        logger.info(f"Running command: {' '.join(args)}")
        
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"Exiftool error: {result.stderr}")
            return False
        
        logger.info(f"Successfully wrote metadata to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing metadata to {file_path}: {e}")
        return False

def backup_file(file_path: str) -> Optional[str]:
    """
    Create a backup of a file before modifying it.
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to the backup file if successful, None otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    try:
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup of {file_path} at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup of {file_path}: {e}")
        return None
