#!/usr/bin/python3
"""
Basic tests for tag-writer application.

This script tests that the basic components of the tag-writer
application can be imported and initialized correctly.
"""

import os
import sys
import unittest

# Add the parent directory to the path to allow importing the tag_writer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class BasicImportTest(unittest.TestCase):
    """Test that the tag-writer package can be imported and basic components initialized."""
    
    def test_import_modules(self):
        """Test that key modules can be imported."""
        # Test importing main modules
        try:
            from tag_writer import main
            self.assertTrue(True, "Main module imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")
            
        # Test importing utils modules
        try:
            from tag_writer.utils import config
            from tag_writer.utils import file_operations
            from tag_writer.utils import image_processing
            self.assertTrue(True, "Utils modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import utils modules: {e}")
            
        # Test importing models modules
        try:
            from tag_writer.models import metadata
            self.assertTrue(True, "Models modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import models modules: {e}")
    
    def test_initialize_metadata_manager(self):
        """Test that the MetadataManager can be initialized."""
        try:
            from tag_writer.models.metadata import MetadataManager
            
            # Initialize the metadata manager
            metadata_manager = MetadataManager()
            
            # Test basic operations
            metadata_manager.set_field("Headline", "Test Headline")
            self.assertEqual(metadata_manager.get_field("Headline"), "Test Headline",
                             "MetadataManager should store and retrieve fields correctly")
            
            metadata_manager.clear()
            self.assertIsNone(metadata_manager.get_field("Headline"),
                              "MetadataManager clear should remove all fields")
                              
            self.assertTrue(True, "MetadataManager initialized and tested successfully")
        except Exception as e:
            self.fail(f"Failed to initialize or test MetadataManager: {e}")
    
    def test_initialize_config(self):
        """Test that the config module can be initialized and accessed."""
        try:
            from tag_writer.utils.config import config
            
            # Test that the config object exists and has basic attributes
            self.assertIsNotNone(config, "Config singleton should exist")
            self.assertIsNotNone(config.app_name, "Config should have app_name attribute")
            self.assertIsNotNone(config.app_version, "Config should have app_version attribute")
            
            # Test setting and getting a config value
            original_zoom = config.ui_zoom_factor
            config.ui_zoom_factor = 1.2
            self.assertEqual(config.ui_zoom_factor, 1.2, "Config should allow setting and getting values")
            
            # Restore original value
            config.ui_zoom_factor = original_zoom
            
            self.assertTrue(True, "Config initialized and tested successfully")
        except Exception as e:
            self.fail(f"Failed to initialize or test config: {e}")

if __name__ == "__main__":
    unittest.main()

