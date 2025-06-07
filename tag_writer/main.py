#!/usr/bin/python3
"""
Main entry point for tag-writer application.

This module initializes the application, processes command-line arguments,
and starts the main event loop.
"""

import os
import sys
import argparse
import logging
import wx

from tag_writer.ui.main_frame import MainFrame
from tag_writer.utils.config import config

# Set up logging
logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(description="Tag Writer - Image Metadata Editor")
    parser.add_argument("file", nargs="?", help="Image file to open")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Show version and exit if requested
    if args.version:
        print(f"Tag Writer v{config.app_version}")
        return 0
    
    # Initialize wxPython app
    app = wx.App(False)
    
    # Create main frame
    frame = MainFrame(title=f"Tag Writer v{config.app_version}")
    frame.Show()
    
    file_loaded = False
    
    # Load file if specified on command line
    if args.file:
        if os.path.exists(args.file):
            frame.load_file(args.file)
            file_loaded = True
        else:
            logger.error(f"File not found: {args.file}")
            wx.MessageBox(f"File not found: {args.file}", "Error", wx.OK | wx.ICON_ERROR)
    
    # If no file specified on command line, load the most recent file
    if not file_loaded and config.recent_files:
        most_recent_file = config.recent_files[0]
        if os.path.exists(most_recent_file):
            logger.info(f"Loading most recent file: {most_recent_file}")
            frame.load_file(most_recent_file)
        else:
            logger.warning(f"Most recent file no longer exists: {most_recent_file}")
    
    # Start the main event loop
    app.MainLoop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
