# Tag Writer User Guide

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [User Interface](#user-interface)
- [Metadata Fields](#metadata-fields)
- [Common Tasks](#common-tasks)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Frequently Asked Questions](#frequently-asked-questions)

## Introduction

Tag Writer is a specialized tool designed for photographers, archivists, and digital content managers who need to add or edit metadata in image files. It provides a user-friendly interface for managing IPTC and EXIF metadata in JPG, TIFF, and PNG images.

IPTC metadata allows you to embed important information directly into your image files, including:
- Title and description information
- Creator and copyright details
- Keywords and categories
- Creation date and location

This metadata stays with your files and can be read by most image management software, making it valuable for archiving, publishing, and rights management.

## Installation

### System Requirements
- Windows, macOS, or Linux operating system
- Python 3.8 or higher
- ExifTool (must be installed separately)

### Installing ExifTool
Tag Writer uses Phil Harvey's ExifTool for reading and writing metadata. You must install ExifTool before using Tag Writer:

- **Windows**: Download from [exiftool.org](https://exiftool.org) and add to your PATH
- **macOS**: Install via Homebrew with `brew install exiftool`
- **Linux**: Install via your package manager, e.g., `sudo apt install exiftool`

### Installing Tag Writer

#### From PyPI (Recommended)
```bash
pip install tag-writer
```

#### From Source
```bash
git clone https://github.com/yourusername/tag-writer.git
cd tag-writer
pip install -e .
```

## Getting Started

### Launching the Application
- **Command line**: Run `tag-writer` in your terminal
- **With a file**: Run `tag-writer path/to/image.jpg` to open a specific file
- **Development mode**: Run `python run-tag-writer.py` from the project directory

### Basic Workflow
1. Open an image file using File → Open or the Select File button
2. Edit metadata fields in the left panel
3. Click "Write Metadata" to save changes to the image file
4. Use the navigation buttons to move to the next image

## User Interface

Tag Writer features a clean, intuitive interface divided into several main components:

### Main Window
- **Menu Bar**: Access to all application functions
- **Toolbar**: Quick access to common actions
- **Metadata Panel**: Edit image metadata (left side)
- **Image Viewer**: Preview the current image (right side)
- **Status Bar**: Displays current status and file information

## Menu Options
- **File**: Open images, access recent files and directories, save metadata, exit
- **Edit**: Clear fields, export/import metadata as JSON, set today's date, rotate images
- **View**: View all metadata tags, select themes, toggle dark mode
- **Help**: Access help documentation, about information, license details

### Keyboard Shortcuts
- **Ctrl+O**: Open file
- **Ctrl+S**: Save metadata
- **Ctrl+L**: Clear all fields
- **Ctrl+D**: Toggle dark mode
- **Left/Right Arrow**: Navigate between images in the directory

## Metadata Fields

Tag Writer supports the following IPTC metadata fields:

### Basic Information
- **Headline**: A brief title or headline for the image (max 256 characters)
- **Caption/Abstract**: Detailed description of the image content (max 1000 characters)
- **Object Name**: A short identifier or reference name for the image

### Creator Information
- **By-line**: Name of the image creator or photographer
- **By-line Title**: Title or position of the creator
- **Writer/Editor**: Name of the person who wrote the caption/description
- **Credit**: Credit line for the image, often the photographer or agency
- **Source**: Original source of the image

### Rights Information
- **Copyright Notice**: Copyright statement for the image
- **Date Created**: Date the image was created (format: YYYY:MM:DD)

## Common Tasks

### Adding Metadata to a New Image
1. Open the image using File → Open
2. Fill in the metadata fields in the left panel
3. Click "Write Metadata" to save
4. A confirmation dialog will appear when complete

### Editing Existing Metadata
1. Open an image that already contains metadata
2. Existing metadata will automatically populate the fields
3. Edit the fields as needed
4. Click "Write Metadata" to update the file

### Batch Processing with JSON
1. Set up metadata for one image
2. Use Edit → Export to JSON to save the metadata
3. Open another image
4. Use Edit → Import from JSON to apply the saved metadata
5. Click "Write Metadata" to save changes

### Working with Multiple Images
1. Open any image from a directory
2. Use navigation methods:
   - Click "Previous" and "Next" buttons in the toolbar
   - Use Left/Right arrow keys for quick navigation
   - Navigation loops (first image wraps to last, and vice versa)
3. Edit metadata for each image
4. Click "Write Metadata" before moving to the next image

### Arrow Key Navigation
Tag Writer provides convenient keyboard navigation:
- **Left Arrow**: Navigate to the previous image in the directory
- **Right Arrow**: Navigate to the next image in the directory
- **Looping**: When you reach the last image and press Right, it loops to the first image
- **Works everywhere**: Arrow keys work from any part of the interface
- **Quick editing**: Perfect for rapidly moving through images while editing metadata

## Advanced Features

### Image Rotation
Tag Writer can rotate images while preserving metadata:
1. Open an image
2. Go to Edit → Rotate Image
3. Choose "Rotate Clockwise" or "Rotate Counter-clockwise"
4. Confirm the rotation
5. The image will be rotated and metadata preserved

### Full-Size Image Preview
1. Open an image
2. Click the "View Full Image" button
3. Use mouse wheel or +/- keys to zoom
4. Click and drag to pan around the image
5. Use "Fit to Window" for optimal viewing

### UI Zoom Adjustment
If the interface text is too small or large:
1. Use the zoom controls in the toolbar (+ and - buttons)
2. Or use keyboard shortcuts: Ctrl++ to zoom in, Ctrl+- to zoom out

### Recent Files and Directories
Tag Writer keeps track of your recently used files and directories:
1. **Recent Files**: Access your last 5 opened files via File → Recent Files
2. **Recent Directories**: Quickly return to directories via File → Recent Directories
3. Click any recent directory to open the first image in that folder
4. Use "Clear Recent Files" or "Clear Recent Directories" to reset the lists

### Theme Selection
Choose from multiple professional themes:
1. Go to View → Theme to open the theme selection dialog
2. Available themes include:
   - **Default Light**: Clean, modern light theme
   - **Dark**: Elegant dark theme (new default)
   - **Solarized Light/Dark**: Popular programmer themes
   - **High Contrast**: Accessibility-focused black and white
   - **Monokai**: Rich editor theme with vibrant colors
   - **GitHub Dark**: Authentic GitHub dark mode experience
3. Preview themes in real-time before applying
4. Your theme choice is automatically saved

### Dark Mode Toggle
Quickly switch between light and dark themes:
1. Go to View → Toggle Dark Mode
2. Or use the keyboard shortcut Ctrl+D
3. This switches between Default Light and Dark themes
4. Your preference will be remembered between sessions

## Troubleshooting

### Common Issues

#### "Error reading metadata"
- Ensure ExifTool is properly installed and in your PATH
- Check that the file is not corrupted or read-only
- Try creating a copy of the file and opening the copy

#### "Error saving metadata"
- Verify you have write permissions for the file and directory
- Check if the file is open in another application
- Ensure there is sufficient disk space

#### "No image displayed"
- Confirm the file is a supported format (JPG, TIFF, PNG)
- Check if the file can be opened in other image viewers
- Verify the file is not corrupted

### Logs
Tag Writer creates log files that can help diagnose issues:
- On Windows: Check `%APPDATA%\tag-writer\logs`
- On macOS/Linux: Check `~/.tag-writer/logs`

## Frequently Asked Questions

### What image formats are supported?
Tag Writer supports JPEG, TIFF, and PNG formats. RAW formats are not directly supported.

### Does Tag Writer modify my original images?
Yes, Tag Writer writes metadata directly to your image files. However, it creates a backup before making changes, which can be found in the same directory with "_backup_" in the filename.

### Can I use Tag Writer for batch processing?
Tag Writer doesn't have direct batch processing capabilities, but you can use the JSON export/import feature to apply the same metadata to multiple images.

### How do I report bugs or request features?
Please submit issues on our GitHub repository: https://github.com/yourusername/tag-writer/issues

---

This documentation is for Tag Writer version 0.07n. For the latest documentation, please visit our [GitHub repository](https://github.com/juren53/tag-writer).

### Recent Changes in Version 0.07n
- Added Additional Info field for contact information and URLs using IPTC:Contact
- Enhanced Help menu with local file priority and GitHub URL fallback
- Improved User Guide and Glossary access with automatic fallback system
- Better error handling and user feedback for documentation access
- Full integration of Additional Info field with all existing functionality

For complete version history, see the [CHANGELOG.md](../CHANGELOG.md) file.

