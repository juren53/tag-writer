# Tag Writer - AI Development Guidelines (WARP.md)

This document provides guidance for AI agents working with the Tag Writer repository, a PyQt6-based IPTC metadata editor for image files.

## Project Overview

Tag Writer is a free, open-source desktop application for viewing and editing IPTC metadata in image files (JPEG, TIFF, PNG). It's designed for photographers, archivists, and digital asset managers who need to manually tag images when metadata cannot be pulled from online databases.

### Core Technology Stack
- **Language**: Python 3
- **GUI Framework**: PyQt6
- **Metadata Processing**: ExifTool (via python-exiftool)
- **Image Processing**: Pillow (PIL)
- **Configuration**: JSON-based user settings
- **Packaging**: AppImage for Linux distribution

### Current Version
- **Version**: 0.1.2 (as of 2026-01-01)
- **Main File**: `tag-writer.py`
- **Architecture**: Single-file PyQt6 application with integrated functionality

## Development Guidelines

### Code Architecture & Patterns

#### Application Structure
- **Main Application Class**: `BattMonCrossPlatform` (historically named, handles UI and core logic)
- **Configuration Management**: `Config` class with JSON persistence at `~/.tag_writer_config.json`
- **Image Handling**: Integrated image viewer with thumbnail generation and metadata display
- **Metadata Operations**: ExifTool-based IPTC tag reading/writing with comprehensive error handling

#### Key Design Patterns
- **Single File Architecture**: All functionality integrated in `tag-writer.py` for simplicity
- **Configuration Persistence**: JSON-based settings with automatic save/load
- **Cross-Platform Compatibility**: Windows, Linux, and macOS support
- **Theme System**: Light/Dark mode with proper PyQt6 styling
- **Recent Files Management**: User-friendly file and directory history

### Development Standards

#### Code Style
- Follow PEP 8 conventions
- Use descriptive variable names and comprehensive docstrings
- Implement proper error handling with logging
- Maintain cross-platform compatibility
- Use type hints where appropriate

#### PyQt6 Best Practices
- Use proper signal/slot connections
- Implement responsive UI layouts
- Handle widget lifecycle correctly
- Maintain proper parent-child relationships
- Use appropriate Qt6 enum values (e.g., `Qt.TextFormat.RichText`)

### Key Features & Components

#### IPTC Metadata Fields (Core Functionality)
The application supports standard IPTC metadata fields mapped to Harry S. Truman Library workflows:
- **Headline**: Title/Event name
- **Caption-Abstract**: Description text with dynamic sizing
- **Object Name**: Unique identifier/Accession number
- **By-line**: Photographer name
- **By-line Title**: Photographer's organization
- **Credit**: Institution credit
- **Source**: Collection information
- **Copyright Notice**: Rights and restrictions
- **Writer-Editor**: Archivist/Editor initials

#### Image Processing Features
- **16-bit TIFF Support**: Automatic conversion for display compatibility
- **Thumbnail Generation**: Embedded thumbnail viewing
- **Image Information**: Technical metadata table with color space and bit depth
- **Format Support**: JPEG, TIFF, PNG with comprehensive metadata reading

#### User Interface Components
- **Main Window**: Splitter layout with image viewer and metadata panel
- **Menu System**: File operations, view options, help documentation
- **Status Bar**: ExifTool status, file information, operation feedback
- **Theme Support**: Light/Dark themes with proper styling
- **Keyboard Shortcuts**: Efficient workflow navigation (Ctrl+T for tag viewer, etc.)

### Development Tasks & Patterns

#### Adding New Metadata Fields
1. Update the metadata field definitions in the UI creation methods
2. Add corresponding ExifTool tag mappings
3. Update save/load metadata functions
4. Add validation and error handling
5. Update help documentation and tooltips

#### Image Format Support
- Use Pillow (PIL) for image loading and display
- Handle format-specific metadata through ExifTool
- Implement proper error handling for unsupported formats
- Test with various bit depths and color spaces

#### UI Enhancements
- Follow existing theme system patterns
- Use proper PyQt6 size policies and layouts
- Implement keyboard shortcuts consistently
- Add tooltips for user guidance
- Maintain accessibility standards

### Configuration & Settings

#### Configuration File Structure
```json
{
  "recent_files": ["path1.jpg", "path2.tif"],
  "recent_directories": ["/path/to/dir1", "/path/to/dir2"],
  "last_directory": "/last/used/directory",
  "dark_mode": false,
  "ui_zoom_factor": 1.0,
  "current_theme": "Light",
  "selected_file": "/current/file.jpg",
  "window_geometry": "serialized_geometry",
  "window_maximized": false
}
```

#### Theme Management
- **Theme Files**: Integrated CSS-like styling within the application
- **Dynamic Switching**: Runtime theme changes without restart
- **Form Field Styling**: Proper text colors and focus states for all themes

### Testing & Quality Assurance

#### Testing Approaches
```bash
# Basic functionality test
python3 tag-writer.py

# Test with command-line file argument
python3 tag-writer.py /path/to/test-image.jpg

# Test ExifTool availability
python3 -c "import exiftool; print('ExifTool available')"

# Test dependencies
python3 -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 available')"
```

#### Image Format Testing
- Test with various JPEG compression levels
- Verify 16-bit TIFF handling and conversion
- Test PNG with and without metadata
- Validate metadata preservation during save operations
- Check edge cases (zero-byte images, corrupted files)

#### Cross-Platform Testing
- **Linux**: Test with various desktop environments (GNOME, KDE, XFCE)
- **Windows**: Verify taskbar integration and file associations
- **macOS**: Check menu bar integration and file dialogs

### Build & Distribution

#### AppImage Building
The project includes Warp workflows for automated AppImage creation:

```bash
# Full production build with testing
warp-cli run .warp/workflows/build-appimage.yaml

# Quick development build
warp-cli run .warp/workflows/quick-build.yaml

# Test existing AppImage
warp-cli run .warp/workflows/test-appimage.yaml
```

#### Dependencies for Building
- **Python 3** with PyQt6 installed
- **ExifTool** available in system PATH
- **appimagetool** for Linux AppImage creation
- **Pillow (PIL)** for image processing

#### Manual Build Process
```bash
# Install dependencies
pip install PyQt6 pillow exiftool

# Create AppDir structure
mkdir -p TagWriter.AppDir/usr/bin
cp tag-writer.py TagWriter.AppDir/usr/bin/
cp ICON_tw.png TagWriter.AppDir/

# Build AppImage
./appimagetool TagWriter.AppDir
```

### Error Handling & Debugging

#### Common Issues & Solutions
1. **ExifTool Not Found**: Show clear installation instructions with platform-specific commands
2. **PyQt6 Import Error**: Provide fallback suggestions and installation guidance
3. **Image Loading Failures**: Handle with graceful error messages and format validation
4. **Metadata Write Failures**: Preserve original files and show detailed error information

#### Debugging Techniques
- Use `logging` module with appropriate levels (DEBUG, INFO, ERROR)
- Implement try-catch blocks around critical operations
- Provide detailed error dialogs for user-facing issues
- Log technical details to console for developer debugging

#### Performance Considerations
- **Image Loading**: Use appropriate thumbnail sizes to reduce memory usage
- **Metadata Operations**: Cache metadata where appropriate to avoid repeated ExifTool calls
- **UI Responsiveness**: Use QTimer for periodic updates, avoid blocking operations
- **File Operations**: Handle large directories efficiently with progress indicators

### Security & File Safety

#### Metadata Handling
- Preserve original file timestamps and permissions
- Create backup copies before metadata writes (when configured)
- Validate metadata input to prevent ExifTool injection attacks
- Handle file permissions and access errors gracefully

#### User Data Protection
- Store configuration files with appropriate permissions (user-only access)
- Never log sensitive metadata or file paths in production
- Respect user privacy settings and metadata visibility preferences

### Documentation & Help

#### User Documentation
- **Docs/README.md**: User-facing documentation and setup instructions
- **Docs/user-guide.md**: Comprehensive usage guide with screenshots
- **Docs/tag-writer-help.md**: In-application help content
- **CHANGELOG.md**: Detailed version history and feature documentation

#### Technical Documentation
- **Info/**: Technical reference materials and development notes
- **REFACTORING-SUMMARY.md**: Architecture decisions and code organization
- **Keyboard-Shortcuts.md**: Complete shortcut reference

### Integration & Workflow

#### Command-Line Integration
- Accept image file paths as arguments for "Open with" functionality
- Support batch processing patterns (future enhancement)
- Enable scripting integration through command-line interface

#### Desktop Integration
- **File Associations**: Register as handler for supported image formats
- **System Tray**: Consider background operation for frequent metadata editing
- **Recent Files**: Integration with system recent files where applicable

---

## Quick Reference

### Essential Commands
```bash
# Run application
python3 tag-writer.py

# Run with specific file
python3 tag-writer.py image.jpg

# Check dependencies
python3 -c "import PyQt6, exiftool, PIL; print('All dependencies available')"

# Build AppImage
warp-cli run .warp/workflows/build-appimage.yaml
```

### Key Files
- `tag-writer.py` - Main application (4000+ lines)
- `CHANGELOG.md` - Complete version history
- `Docs/` - User documentation and help files
- `.warp/workflows/` - Automated build scripts
- `archive/` - Previous versions and development history

### Development Focus Areas
- **Cross-platform compatibility** - Windows, Linux, macOS support
- **User experience** - Intuitive metadata editing workflow
- **Performance** - Efficient image and metadata handling
- **Reliability** - Robust error handling and data preservation
- **Documentation** - Comprehensive user and developer guides

This project prioritizes professional archival workflows, cross-platform compatibility, and user-friendly metadata management for digital asset professionals.
