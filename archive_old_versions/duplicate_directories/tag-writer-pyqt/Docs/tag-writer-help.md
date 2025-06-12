# Tag Writer User Guide

**Version 0.06b**

## Overview

Tag Writer is a free, open-source application designed to view and edit IPTC metadata in image files (JPG and TIF formats). This tool is particularly useful when metadata cannot be pulled from an online database and needs to be entered manually.

The application provides a simple graphical user interface for editing common IPTC metadata fields, allowing photographers, archivists, and digital asset managers to properly tag their images with essential information.

![Tag Writer Main Window](https://github.com/juren53/tag-writer/raw/main/Docs/images/main-window.png)

## Table of Contents

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Dependencies](#dependencies)
- [Interface Overview](#interface-overview)
  - [Main Window](#main-window)
  - [Menu Structure](#menu-structure)
- [Using Tag Writer](#using-tag-writer)
  - [Selecting Files](#selecting-files)
  - [Viewing Existing Metadata](#viewing-existing-metadata)
  - [Editing Metadata](#editing-metadata)
  - [Writing Metadata](#writing-metadata)
  - [Exporting to JSON](#exporting-to-json)
  - [Importing from JSON](#importing-from-json)
  - [Viewing All Metadata Tags](#viewing-all-metadata-tags)
  - [Rotating Images](#rotating-images)
  - [Image Preview](#image-preview)
- [IPTC Metadata Fields](#iptc-metadata-fields)
- [Command-Line Usage](#command-line-usage)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Missing Dependencies](#missing-dependencies)
- [License Information](#license-information)
- [Support and Feedback](#support-and-feedback)

## Installation

### Requirements

- Python 3.x
- Operating systems: Linux, macOS, or Windows

### Dependencies

Tag Writer requires the following Python libraries:

1. **exiftool** - The Python wrapper for ExifTool, which is used to read and write metadata
   ```
   pip install pyexiftool
   ```

2. **PIL/Pillow** - The Python Imaging Library, used for thumbnail display and image preview
   ```
   pip install Pillow
   ```

3. **ExifTool** - The external program that must be installed separately
   - On Debian/Ubuntu: `sudo apt-get install libimage-exiftool-perl`
   - On macOS with Homebrew: `brew install exiftool`
   - On Windows: Download from [ExifTool website](https://exiftool.org/)

Note: Tag Writer can run with limited functionality if PIL/Pillow is not installed, but thumbnail and image previews will not be available.

## Interface Overview

### Main Window

The Tag Writer main window is divided into several key areas:

- **Menu Bar** - Contains File, Edit, View, and Help menus
- **Control Buttons** - "Select File" and "Write Metadata" buttons
- **Metadata Fields** - Input fields for various IPTC metadata
- **Status Bar** - Shows operation status messages
- **Thumbnail Display** - Shows a preview of the selected image with dimensions
- **Version Information** - Displays the current version and dependency status

### Menu Structure

#### File Menu
- **Open** - Select an image file to edit
- **Recently accessed** - Submenu showing up to 5 recently accessed files
- **Save** - Save metadata to the current file
- **Exit** - Close the application

#### Edit Menu
- **Clear Fields** - Clear all metadata entry fields
- **Export IPTC tags** - Export the current metadata to a JSON file
- **Import IPTC tags** - Import metadata from a JSON file
- **Rotate Clockwise** - Rotate image 90° clockwise (creates backup)
- **Rotate Counter-clockwise** - Rotate image 90° counter-clockwise (creates backup)

#### View Menu
- **Show ALL Metatags** - Display all metadata tags for the current image

#### Help Menu
- **About** - Display information about Tag Writer
- **License** - Show license information
- **Usage Guide** - Open this help document in a web browser

## Using Tag Writer

### Selecting Files

There are several ways to select an image file for editing:

1. Click the "Select File" button in the main window
2. Use the File → Open menu option
3. Select a file from the File → Recently accessed submenu
4. Provide a file path as a command-line argument when launching the application

After selecting a file, the file name will be displayed, and any existing metadata will be loaded into the form fields.

### Viewing Existing Metadata

When you select an image file, Tag Writer automatically reads the IPTC metadata from the file and populates the form fields with the existing values. This allows you to see what metadata is already associated with the image.

The thumbnail preview (if available) shows a small version of the image to confirm you're working with the correct file.

### Editing Metadata

To edit metadata:

1. Select an image file
2. Modify the values in any of the input fields
3. Click "Write Metadata" to save the changes to the file

#### Caption Abstract Field

The Caption Abstract field has been enhanced with the following features:

- Character limit increased to 1000 characters (from 256)
- Character counter showing current usage (e.g., "150/1000 characters")
- Text color changes to yellow when exceeding 256 characters as a visual indicator
- Improved cursor position handling to maintain your editing position when typing

### Writing Metadata

After editing the metadata fields, click the "Write Metadata" button to save the changes to the image file. A confirmation message will appear in the status bar at the bottom of the window.

Important: Tag Writer does not create backup files by default. Any changes you make will overwrite the existing metadata in the file.

### Exporting to JSON

You can export the metadata from the current image to a JSON file for backup or processing in other applications:

1. Select an image file
2. Go to Edit → Export IPTC tags
3. Choose a location to save the JSON file

### Importing from JSON

You can import metadata from a previously exported JSON file to apply it to a different image:

1. Select an image file that will receive the metadata
2. Go to Edit → Import IPTC tags
3. Choose the JSON file containing the metadata
4. Click "Write Metadata" to save the imported metadata to the image file

This feature is useful for applying the same metadata to multiple images or for restoring previously backed up metadata.

### Viewing All Metadata Tags

Tag Writer now allows you to view all metadata tags present in an image, not just the IPTC fields that can be edited:

1. Select an image file
2. Go to View → Show ALL Metatags
3. A new window will open displaying all metadata organized by category

This comprehensive view includes EXIF, XMP, IPTC, and other metadata formats, providing valuable technical information about the image.

### Rotating Images

Tag Writer provides image rotation functionality that preserves all metadata:

- **Edit → Rotate Clockwise**: Rotates the image 90° clockwise
- **Edit → Rotate Counter-clockwise**: Rotates the image 90° counter-clockwise

When you rotate an image:
1. A backup of the original image is created automatically
2. The image is rotated using FFmpeg
3. All IPTC and other metadata is preserved in the rotated image
4. The rotated image replaces the original file

### Image Preview

If PIL/Pillow is installed, Tag Writer provides image preview functionality:

1. **Thumbnail View** - A small preview appears in the main window
2. **Full Image View** - Click on the thumbnail to open a larger view of the image
   - The full view window shows the image dimensions
   - Use the minimize and maximize buttons to control the window
   - Click anywhere on the image or press the Close button to close the view

## IPTC Metadata Fields

Tag Writer supports editing the following IPTC metadata fields:

| Field | Description | Example |
|-------|-------------|---------|
| Headline | A brief synopsis of the content | "Sunset over Mount Rainier" |
| Credit | The provider of the image | "Reuters" |
| Object Name (Unique ID) | A unique identifier for the image | "IMG20250401_12345" |
| Caption Abstract | A textual description of the content (up to 1000 characters) | "A colorful sunset photographed from Paradise viewpoint..." |
| Writer Editor | Person who wrote the caption | "Jane Smith" |
| By-line (Photographer) | Name of the photographer | "John Doe" |
| Source | Original owner of the copyright | "National Geographic" |
| Date Created | The date the image was created (YYYY-MM-DD) | "2025-04-01" |
| Copyright Notice | Copyright statement | "© 2025 John Doe. All rights reserved." |

## Command-Line Usage

Tag Writer can be launched from the command line with the following options:

```
python tag-writer.py [file_path] [-d DIRECTORY] [-v/--version]
```

Arguments:
- `file_path` - (Optional) Path to an image file to open immediately
- `-d`, `--directory` - Specify a starting directory
- `-v`, `--version` - Show version information and exit

Examples:
```
# Launch with GUI only
python tag-writer.py

# Launch and open a specific file
python tag-writer.py /path/to/image.jpg

# Launch with a specific starting directory
python tag-writer.py -d /path/to/photos/directory

# Display version information
python tag-writer.py --version
```

## Troubleshooting

### Common Issues

**Issue: "No module named 'exiftool'"**  
Solution: Install the pyexiftool module using `pip install pyexiftool`

**Issue: "No module named 'PIL'"**  
Solution: Install Pillow using `pip install Pillow`. The application will run without it, but image previews will be disabled.

**Issue: "Error executing exiftool"**  
Solution: Ensure that ExifTool is installed on your system and accessible in your PATH.

**Issue: No thumbnails or image previews**  
Solution: Verify that both PIL and ImageTk are properly installed. On some systems, additional packages may be required for ImageTk functionality.

**Issue: Image rotation doesn't work**  
Solution: Make sure FFmpeg is installed on your system and available in your PATH.

**Issue: Cursor jumps when editing Caption Abstract field**  
Solution: This has been fixed in version 0.06b. Update to the latest version.

### Missing Dependencies

Tag Writer will operate in reduced functionality mode if certain dependencies are missing:

- Without **PIL/Pillow**: No thumbnail or image preview functionality
- Without **ImageTk** (part of PIL): No image display, even if PIL is installed
- Without **ExifTool**: The application will not run
- Without **FFmpeg**: Image rotation functionality will not be available

The application displays the status of these dependencies in the version label at the bottom of the window.

## License Information

Tag Writer is free software, distributed under the terms of the GNU General Public License version 3 or later.

```
tag-writer is free software: you can redistribute it and/or modify it under the terms 
of the GNU General Public License as published by the Free Software Foundation; either 
version 3 of the License, or (at your option) any later version.

tag-writer is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with tag-writer. 
If not, see: https://www.gnu.org/licenses/
```

Source code is available at: https://github.com/juren53/tag-writer/blob/main/code/tag-writer.py

## Support and Feedback

For bug reports, feature requests, or general feedback, please open an issue on the GitHub repository:

https://github.com/juren53/tag-writer/issues

---

*This documentation was last updated on May 31, 2025*

