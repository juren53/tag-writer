#!/usr/bin/python3
"""
Metadata model module for tag-writer application.

This module provides classes and functions for handling image metadata:
- Parsing and formatting metadata
- Storing metadata in a structured way
- Converting between different metadata formats
"""

import os
import logging
import json
import datetime
import subprocess
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MetadataManager:
    """
    Class to manage image metadata operations.
    
    This class encapsulates all metadata-related functionality and maintains
    the current state of metadata being edited.
    """
    
    # Mapping of display field names to exiftool field names
    FIELD_MAPPING = {
        "Headline": "Headline",
        "Caption-Abstract": "Caption-Abstract",
        "Credit": "Credit",
        "ObjectName": "ObjectName",
        "Writer-Editor": "Writer-Editor",
        "By-line": "By-line",
        "By-lineTitle": "By-lineTitle",
        "Source": "Source",
        "DateCreated": "DateCreated",
        "Copyright": "Copyright",
        "Object Name": "ObjectName",  # Added for compatibility with UI labels
        "By-line Title": "By-lineTitle",  # Added for compatibility with UI labels
        "Date Created": "DateCreated",  # Added for compatibility with UI labels
        "Copyright Notice": "Copyright"  # Added for compatibility with UI labels
    }
    
    # Field mappings from the original application
    FIELD_SEARCH_MAPPINGS = {
        'Headline': ['IPTC:Headline', 'XMP-photoshop:Headline', 'XMP:Headline', 'XMP:Title'],
        'Caption-Abstract': ['IPTC:Caption-Abstract', 'XMP:Description', 'EXIF:ImageDescription'],
        'Credit': ['IPTC:Credit', 'XMP:Credit', 'XMP-photoshop:Credit'],
        'Object Name': ['IPTC:ObjectName', 'IPTC:Object Name', 'XMP:Title'],
        'Writer-Editor': ['IPTC:Writer-Editor', 'XMP:CaptionWriter', 'XMP-photoshop:CaptionWriter'],
        'By-line': ['IPTC:By-line', 'XMP:Creator', 'EXIF:Artist'],
        'By-line Title': ['IPTC:By-lineTitle', 'XMP:AuthorsPosition', 'XMP-photoshop:AuthorsPosition'],
        'Source': ['IPTC:Source', 'XMP:Source', 'XMP-photoshop:Source'],
        'Date Created': ['IPTC:DateCreated', 'XMP:DateCreated', 'XMP-photoshop:DateCreated'],
        'Copyright Notice': ['IPTC:CopyrightNotice', 'XMP:Rights', 'EXIF:Copyright', 'Copyright', 'Copyright Notice']
    }
    
    def __init__(self):
        """Initialize metadata manager with empty metadata."""
        self.current_metadata: Dict[str, Any] = {}
        self.modified: bool = False
        self.source_file: Optional[str] = None
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load metadata from a file.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if successful, False otherwise
        """
        # Import here to avoid circular imports
        from tag_writer.utils.file_operations import read_metadata
        
        try:
            metadata = read_metadata(file_path)
            if metadata:
                # Process the raw metadata to extract relevant fields
                self.current_metadata = self.process_metadata(metadata)
                self.source_file = file_path
                self.modified = False
                logger.info(f"Loaded metadata from {file_path}")
                return True
            else:
                logger.warning(f"No metadata found in {file_path}")
                self.clear()
                self.source_file = file_path
                return False
        except Exception as e:
            logger.error(f"Error loading metadata from {file_path}: {e}")
            return False
    
    def process_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw metadata to extract and normalize relevant fields.
        
        Args:
            raw_metadata: Raw metadata dictionary from exiftool
            
        Returns:
            Processed metadata with relevant fields
        """
        processed = {}
        
        # Extract fields based on the field mappings
        for field, possible_names in self.FIELD_SEARCH_MAPPINGS.items():
            for name in possible_names:
                if name in raw_metadata:
                    # Map to our standard field names
                    if field == "Object Name":
                        processed["ObjectName"] = raw_metadata[name]
                    elif field == "By-line Title":
                        processed["By-lineTitle"] = raw_metadata[name]
                    elif field == "Date Created":
                        processed["DateCreated"] = raw_metadata[name]
                    elif field == "Copyright Notice":
                        processed["Copyright"] = raw_metadata[name]
                    else:
                        processed[field] = raw_metadata[name]
                    logger.debug(f"Found '{field}' in '{name}': {raw_metadata[name]}")
                    break
        
        # Also try direct field names
        for display_name, exif_name in self.FIELD_MAPPING.items():
            if display_name not in processed and exif_name in raw_metadata:
                processed[display_name] = raw_metadata[exif_name]
        
        return processed
    
    def save_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        Save metadata to a file.
        
        Args:
            file_path: Path to the image file (uses source_file if None)
            
        Returns:
            True if successful, False otherwise
        """
        # Import here to avoid circular imports
        from tag_writer.utils.file_operations import backup_file
        
        target_file = file_path or self.source_file
        if not target_file:
            logger.error("No target file specified and no source file set")
            return False
        
        try:
            # Create backup
            backup_file(target_file)
            
            # Write metadata using exiftool directly
            success = self.write_metadata_with_exiftool(target_file)
            
            if success:
                self.modified = False
                logger.info(f"Saved metadata to {target_file}")
                return True
            else:
                logger.error(f"Failed to save metadata to {target_file}")
                return False
        except Exception as e:
            logger.error(f"Error saving metadata to {target_file}: {e}")
            return False
    
    def write_metadata_with_exiftool(self, file_path: str) -> bool:
        """
        Write metadata to a file using exiftool directly.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare command arguments
            args = ["exiftool"]
            
            # Map display field names to exiftool field names
            metadata_to_write = {}
            for display_name, value in self.current_metadata.items():
                if display_name in self.FIELD_MAPPING and value:
                    exif_name = self.FIELD_MAPPING[display_name]
                    metadata_to_write[exif_name] = value
            
            # Add each metadata field
            for exif_name, value in metadata_to_write.items():
                if value:
                    args.append(f"-{exif_name}={value}")
            
            # Add overwrite original flag
            args.append("-overwrite_original")
            
            # Add file path at the end
            args.append(file_path)
            
            # Log the command for debugging
            logger.info(f"ExifTool write command: {' '.join(args)}")
            
            # Execute command
            result = subprocess.run(args, capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                logger.error(f"ExifTool error: {result.stderr}")
                return False
            
            logger.info(f"ExifTool write result: {result.stdout}")
            return True
        except Exception as e:
            logger.error(f"Error executing ExifTool: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all metadata."""
        self.current_metadata = {}
        self.modified = False
        logger.info("Cleared metadata")
    
    def set_field(self, field_name: str, value: Any) -> None:
        """
        Set a metadata field value.
        
        Args:
            field_name: Name of the metadata field
            value: Value to set
        """
        if field_name in self.current_metadata and self.current_metadata[field_name] == value:
            return  # No change
        
        self.current_metadata[field_name] = value
        self.modified = True
        logger.info(f"Set metadata field {field_name}")
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """
        Get a metadata field value.
        
        Args:
            field_name: Name of the metadata field
            default: Default value if field doesn't exist
            
        Returns:
            Field value or default
        """
        return self.current_metadata.get(field_name, default)
    
    def export_to_json(self, file_path: str) -> bool:
        """
        Export metadata to a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.current_metadata, f, indent=2)
            logger.info(f"Exported metadata to JSON: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting metadata to JSON {file_path}: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """
        Import metadata from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                imported_metadata = json.load(f)
            
            self.current_metadata = imported_metadata
            self.modified = True
            logger.info(f"Imported metadata from JSON: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error importing metadata from JSON {file_path}: {e}")
            return False
    
    def get_field_names(self) -> List[str]:
        """
        Get a list of all metadata field names.
        
        Returns:
            List of field names
        """
        return list(self.current_metadata.keys())
    
    def is_modified(self) -> bool:
        """
        Check if metadata has been modified.
        
        Returns:
            True if modified, False otherwise
        """
        return self.modified
