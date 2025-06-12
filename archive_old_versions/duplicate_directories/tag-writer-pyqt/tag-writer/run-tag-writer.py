#!/usr/bin/python3
"""
Development runner script for tag-writer application.

This script provides a convenient way to run the tag-writer application
during development without installing it as a package. It adds the current
directory to the Python path so the tag_writer package can be imported.

Usage:
    python run-tag-writer.py [OPTIONS]
    
    For command-line options, see the --help output.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the main function
from tag_writer.main import main

if __name__ == "__main__":
    sys.exit(main())

