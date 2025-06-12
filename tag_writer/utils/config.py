#!/usr/bin/python3
"""
Configuration and settings module for tag-writer application.

This module centralizes all configuration settings and formerly global variables
to provide better organization and easier management.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class to manage application settings and state.
    Replaces global variables with a proper OOP approach.
    """
    
    def __init__(self):
        """Initialize configuration with default values."""
        # Application info
        self.app_name = "Tag Writer"
        self.app_version = "0.07e"
        
        # File management
        self.recent_files: List[str] = []
        self.max_recent_files = 5
        self.selected_file: Optional[str] = None
        self.last_directory: Optional[str] = None
        self.directory_image_files: List[str] = []
        self.current_file_index: int = -1
        
        # Image viewer settings
        self.original_image = None
        self.full_image_original = None
        self.full_image_zoom_factor = 1.0
        
        # UI zoom settings
        self.ui_zoom_factor = 1.0
        
        # Theme settings
        self.dark_mode = False  # Default to light mode
        
        # Load any saved configuration
        self.load_config()
    
    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list.
        
        Args:
            file_path: Path to the file to add
        """
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files.pop()
        
        logger.info(f"Added {file_path} to recent files")
        self.save_config()
    
    def load_config(self) -> None:
        """Load configuration from file if it exists."""
        config_path = os.path.expanduser("~/.tag-writer-config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update attributes from saved config
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config_path = os.path.expanduser("~/.tag-writer-config.json")
        
        try:
            # Save only serializable attributes
            config_data = {
                'recent_files': self.recent_files,
                'max_recent_files': self.max_recent_files,
                'ui_zoom_factor': self.ui_zoom_factor,
                'dark_mode': self.dark_mode,
                'selected_file': self.selected_file,
                'last_directory': self.last_directory
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

# Create a singleton instance
config = Config()
