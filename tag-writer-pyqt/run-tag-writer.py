#!/usr/bin/python3
"""
Runner script for tag-writer application.

This script provides a convenient way to run the tag-writer application
during development without installing it.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the main function
from tag_writer.main import main

if __name__ == "__main__":
    sys.exit(main())
