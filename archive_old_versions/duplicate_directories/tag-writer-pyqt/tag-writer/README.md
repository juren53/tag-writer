# Tag Writer

A Python application for editing image metadata tags, now with a clean, modern UI.

## Overview

Tag Writer allows you to view and edit IPTC metadata in image files. It provides a user-friendly interface for adding titles, descriptions, copyright information, and other metadata to your images.

The application has been completely refactored from its original implementation to follow best practices in Python development, with a modular architecture and clean separation of concerns.

## Features

- **Intuitive UI**: Modern PyQt6-based interface with dark mode support
- **Metadata Editing**: Edit IPTC and EXIF metadata in JPG, TIFF, and PNG files
- **Full-Size Preview**: View images with zoom and pan capabilities
- **Image Navigation**: Browse through all images in a directory
- **Recent Files**: Quick access to recently edited files
- **JSON Export/Import**: Export metadata to JSON for backup or batch processing
- **Image Rotation**: Rotate images while preserving metadata
- **UI Zoom**: Adjust the UI scale to your preference

## Installation

### From PyPI (Recommended)

```bash
pip install tag-writer
```

### From Source

```bash
git clone https://github.com/yourusername/tag-writer.git
cd tag-writer
pip install -e .
```

### Development Mode

To run the application in development mode without installing:

```bash
# From the project root
python -m tag_writer.main
```

Or use the convenience script:

```bash
python run-tag-writer.py
```

## Usage

### GUI Application

1. Launch the application with `tag-writer` command or from your applications menu
2. Use "File > Open" to select an image
3. Edit metadata fields in the left panel
4. Click "Write Metadata" to save changes
5. Use the navigation buttons or arrow keys to browse through images in the same directory

### Command-Line Options

```bash
tag-writer [IMAGE_FILE] [OPTIONS]

Options:
  -v, --verbose    Enable verbose logging
  --version        Show version information
```

## Project Structure

The project follows a clean, modular structure:

```
tag-writer/
├── tag_writer/            # Main package directory
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Entry point
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   └── metadata.py    # Metadata handling logic
│   ├── ui/                # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main application window
│   │   ├── image_viewer.py   # Image viewing components
│   │   └── metadata_panel.py # Metadata editing UI
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration management
│   │   ├── file_operations.py # File handling utilities
│   │   └── image_processing.py # Image manipulation
│   └── resources/         # Application resources
├── docs/                  # Documentation
├── resources/             # External resources (icons, etc.)
├── tests/                 # Unit and integration tests
├── LICENSE                # License file
├── README.md              # This file
├── setup.py               # Installation configuration
└── run-tag-writer.py      # Development runner script
```

## Dependencies

- **PyQt6**: Modern UI framework
- **Pillow**: Image processing library
- **pyexiftool**: Metadata handling (requires ExifTool to be installed)

### External Dependencies

- [ExifTool](https://exiftool.org/) - Must be installed separately and available in your PATH

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Phil Harvey for [ExifTool](https://exiftool.org/)
- PyQt team for the excellent UI framework
- All contributors who have helped improve this project

