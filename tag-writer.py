#!/usr/bin/env python3
"""
Tag Writer - PyQt6 IPTC Metadata Editor

Thin wrapper that launches the modular Tag Writer application.
The actual implementation lives in src/tag_writer/ package.
"""
#-----------------------------------------------------------
# Tag Writer - IPTC Metadata Editor v0.2.0  2026-02-15 2215 CST
#
# A GUI application for entering and writing IPTC metadata tags
# to TIF and JPG images. Designed for free-form metadata tagging
# when metadata cannot be pulled from online databases.
#
# For complete version history and changelog, see CHANGELOG.md
#-----------------------------------------------------------

import os
import sys

# Add src/ directory to Python path so tag_writer package can be found
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from main import main

if __name__ == "__main__":
    sys.exit(main())
