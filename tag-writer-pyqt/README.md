# Tag Writer

A Python application for editing image metadata tags.

## Overview

Tag Writer allows you to view and edit IPTC metadata in image files. It provides a user-friendly interface for adding titles, descriptions, copyright information, and other metadata to your images.

## Refactoring

This application was refactored from a monolithic script into a properly structured Python package with the following improvements:

1. **Modular Architecture**: Code is now organized into logical modules with clear separation of concerns.
2. **Proper OOP Design**: Classes are designed with single responsibilities and clean interfaces.
3. **Elimination of Global Variables**: Global state is now managed through proper class attributes and configuration.
4. **Improved Error Handling**: More specific exception handling with proper error messages.
5. **Code Documentation**: Added docstrings and comments throughout the codebase.

## Project Structure

```
tag-writer/
├── tag_writer/
│   ├── __init__.py
│   ├── main.py              # Entry point and application initialization
│   ├── models/
│   │   ├── __init__.py
│   │   └── metadata.py      # Metadata handling logic
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_frame.py    # Main application window
│   │   ├── image_viewer.py  # Image viewing components
│   │   ├── metadata_panel.py # Metadata editing UI
│   │   └── dialogs.py       # Common dialogs
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_operations.py # File handling utilities
│   │   ├── image_processing.py # Image manipulation
│   │   └── config.py        # Configuration and settings
│   └── resources/           # Icons, templates, etc.
├── setup.py                 # Package installation script
└── run-tag-writer.py        # Development runner script
```

## Installation

### Development Mode

To run the application in development mode:

```bash
./run-tag-writer.py
```

Or:

```bash
python run-tag-writer.py
```

### Installation

To install the package:

```bash
pip install -e .
```

Then run:

```bash
tag-writer
```

## Dependencies

- wxPython (>=4.0.0): UI framework
- Pillow (>=8.0.0): Image processing
- pyexiftool (>=0.5.0): Metadata handling

## Usage

1. Launch the application
2. Use "File > Open" to select an image
3. Edit metadata fields in the left panel
4. Click "Write Metadata" to save changes
5. Use the thumbnail preview and "View Full Image" to inspect the image

## License

[MIT License](LICENSE)
