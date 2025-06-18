# Changelog

All notable changes to the Tag Writer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Enhanced metadata field support
- Batch processing capabilities
- Additional image format support
- Custom metadata templates

## [0.07l] - 2025-06-18

### Changed
- **Modified Arrow Key Behavior** - Changed arrow key functionality for improved usability
  - Up/Down arrow keys now navigate between images (previous/next)
  - Left/Right arrow keys work for cursor movement in text fields
  - More intuitive text editing experience while maintaining keyboard navigation
  - Consistent behavior across all text fields and dialogs
  - Enhanced user experience when editing metadata

## [0.07k] - 2025-06-17

### Fixed
- **Metadata Text Field Focus** - Fixed keyboard focus issues in metadata text fields
  - Arrow keys now work properly for text cursor navigation within all metadata fields
  - Prevents arrow key events from navigating images while editing metadata
  - Enhanced event handling with proper focus management
  - Improved keyboard interaction in all text editing fields
  - Consistent behavior across the entire application

### Enhanced
- **Better Text Editing Experience** - More natural keyboard navigation within text fields
- **Improved Usability** - Text fields properly maintain input focus during editing

## [0.07j] - 2025-06-17

### Fixed
- **Rename File Dialog Focus** - Fixed keyboard focus issues in the Rename File dialog
  - Arrow keys now work properly for text cursor navigation within filename field
  - Text input field now maintains proper focus for keyboard interactions
  - Prevents arrow key events from navigating images while renaming
  - Improved modal dialog behavior with better keyboard handling
  - Enhanced user experience when editing filenames

### Enhanced
- **Improved Text Editing** - Better keyboard interaction when renaming files
- **More Intuitive Dialog Behavior** - Dialog properly captures keyboard focus

## [0.07i] - 2025-06-17

### Added
- **Refresh Feature** - Added ability to refresh current image and metadata
  - Accessible via F5 key from anywhere in the application
  - Available through new "Refresh" option in View menu
  - Reloads image and metadata from disk without changing selection
  - Preserves cursor positions and text selections in metadata fields
  - Provides visual feedback during refresh operation
  - Helpful for seeing changes made by external applications

### Enhanced
- **Improved User Experience** - Easy refresh of current image without renavigation
- **Better Integration** with external editing workflows
- **Keyboard Accessibility** through standard F5 refresh shortcut

## [0.07h] - 2025-06-16

### Fixed
- **Windows Console Window Flashing** - Eliminated brief console window flashes during image loading on Windows
  - Added Windows-specific ExifTool subprocess configuration
  - Implemented `CREATE_NO_WINDOW` and `SW_HIDE` flags for complete console window suppression
  - Created custom `WindowsExifTool` wrapper class that overrides subprocess creation
  - Applied fix to all ExifTool operations: metadata reading, writing, and processing
  - Maintains full ExifTool functionality while preventing visual disruption
  - Platform-specific implementation - only affects Windows systems
  - Clean fallback to standard ExifTool on non-Windows platforms

### Enhanced
- **Improved Windows User Experience** - Application now appears more stable and professional on Windows
- **Seamless Metadata Operations** - No more brief console window interruptions during image processing
- **Cross-Platform Compatibility** - Windows-specific fixes don't affect Linux/macOS functionality

### Technical
- Added `create_exiftool_instance()` function with Windows-specific subprocess configuration
- Implemented custom `WindowsExifTool` class with overridden `run()` method
- Updated all ExifTool usage throughout codebase to use hidden console window version
- Added Windows subprocess creation flags: `CREATE_NO_WINDOW = 0x08000000` and `SW_HIDE = 0`
- Enhanced subprocess startup configuration with `STARTF_USESHOWWINDOW` flag

## [0.07g] - 2025-06-16

### Added
- **Recent Directories Feature** - Track and quickly access last 5 directories where files were opened
  - "Recent Directories" submenu in File menu alongside "Recent Files"
  - Automatic directory tracking when files are opened
  - Click any recent directory to open the first image in that directory
  - "Clear Recent Directories" option to reset the list
  - Persistent storage in configuration file with validation
- **GitHub Dark Theme** - Added GitHub's official dark theme to the theme collection
  - Authentic GitHub dark color palette (#0d1117 background, #c9d1d9 text)
  - Professional dark theme option for developers
  - GitHub blue selection highlights (#388bfd)
  - Consistent dark grays for UI elements

### Changed
- **Default Theme** - Changed default application theme from "Default Light" to "Dark"
  - New installations start with dark theme for better user experience
  - Existing user theme preferences are preserved
  - Fallback theme is now "Dark" instead of "Default Light"

### Enhanced
- **Improved Navigation Workflow** - Recent directories make it easier to return to frequently used image folders
- **Better Default Experience** - Dark theme provides modern, comfortable viewing by default
- **Expanded Theme Collection** - Now includes 8 professional themes including GitHub Dark

### Technical
- Added `recent_directories` list to Config class with automatic cleanup
- Implemented `add_recent_directory()` method with 5-item limit
- Enhanced configuration persistence to include recent directories
- Updated `load_file()` method to automatically track directories
- Added `open_directory()` and `update_recent_directories_menu()` methods
- Modified theme defaults in Config and ThemeManager classes

## [0.07f] - 2025-06-15

### Added
- **Arrow Key Navigation** in main window for convenient image browsing
  - Left arrow key navigates to previous image (same as "< Previous" button)
  - Right arrow key navigates to next image (same as "Next >" button)
  - Application-level event filter prevents default focus movement between UI elements
  - Maintains looping behavior through image directory
- **Automatic Zoom Reset** - UI zoom level resets to 100% on application startup
- **Enhanced Keyboard Navigation** - Arrow keys now provide seamless image navigation

### Changed
- UI zoom factor automatically resets to 1.0 (100%) on startup regardless of saved configuration
- Arrow keys no longer move focus between toolbar buttons, instead trigger image navigation

### Technical
- Added application-level `eventFilter()` method to intercept arrow key events
- Implemented `QApplication.installEventFilter()` for global keyboard event handling
- Enhanced Config class to force zoom reset during initialization

## [0.07e] - 2025-06-12

### Added
- **Comprehensive Theme System** with 7 professional themes:
  - Default Light (clean, modern light theme)
  - Default Dark (elegant dark theme for reduced eye strain)
  - Solarized Light (warm, easy-on-the-eyes light theme)
  - Solarized Dark (popular dark theme with excellent contrast)
  - High Contrast (black background with bright text for accessibility)
  - Monokai (rich editor theme with vibrant colors)
  - Cyberpunk (futuristic neon theme with electric blue accents)
- **ThemeDialog** with real-time preview for easy theme selection
- **Theme persistence** - selected theme is saved and restored between sessions
- **Comprehensive CSS styling** for all UI elements including metadata forms

### Enhanced
- **Improved user experience** with professional visual themes
- **Better accessibility** with high contrast and dark mode options
- **Consistent theming** across all application components
- **Real-time theme preview** in selection dialog

### Technical
- Added `ThemeManager` class for centralized theme management
- Implemented comprehensive CSS stylesheet generation system
- Enhanced configuration system to include theme preferences
- Added theme application to all PyQt6 widgets

## [0.07d] - 2025-06-09

### Added
- **Image Navigation in Full Image Window** with keyboard shortcuts
  - Left/Right arrow keys for navigation
  - Synchronization with main window selection
  - Seamless navigation without closing full image viewer
- **Enhanced Full Image Viewer** with improved navigation controls

### Enhanced
- **Better user experience** in full image viewing mode
- **Keyboard shortcuts** for efficient image browsing
- **Synchronized navigation** between main window and full image viewer

## [0.07c] - 2025-06-09

### Fixed
- **Full Image Window improvements**:
  - Added maximize/minimize buttons to window title bar
  - Improved scroll bars functionality
  - Better window controls and user interaction

### Enhanced
- **Improved window management** for full image viewing
- **Better scroll bar behavior** for large images
- **Enhanced window controls** with standard minimize/maximize functionality

## [0.07b] - 2025-06-09

### Fixed
- **Resolution Detection** using EXIF metadata
  - Improved accuracy of image resolution information
  - Better handling of various image formats
  - Enhanced metadata extraction reliability

### Enhanced
- **More accurate image information display**
- **Improved EXIF metadata processing**
- **Better image format compatibility**

## [0.07a] - 2025-05-31

### Changed
- **Complete Framework Migration**: Converted from wxPython to PyQt6
  - Modern, cross-platform GUI framework
  - Improved performance and stability
  - Better theme and styling support
  - Enhanced image handling capabilities

### Technical
- **Major architectural change** from wxPython to PyQt6
- **Redesigned UI components** using PyQt6 widgets
- **Improved image processing** with PyQt6 image handling
- **Enhanced cross-platform compatibility**

## [0.06b] - 2025-05-30

### Fixed
- **Caption Abstract Text Box Editor** bug fixes
  - Improved text editing functionality
  - Better handling of large text content
  - Enhanced user input validation

## [0.06a] - 2025-05-30

### Added
- **View/List All Tags Menu Item**
  - Comprehensive metadata tag viewing
  - Complete IPTC field display
  - Enhanced metadata inspection capabilities

### Enhanced
- **Better metadata visibility** and inspection tools
- **Comprehensive tag listing** functionality

## [0.05d] - 2025-05-28

### Enhanced
- **Caption Abstract Field** expanded to 1000 characters
  - Increased capacity for detailed descriptions
  - Better support for comprehensive metadata

## [0.05c] - 2025-05-27

### Enhanced
- **General improvements** and bug fixes
- **Code optimization** and stability improvements

## [0.05b] - 2025-05-27

### Enhanced
- **Performance improvements**
- **UI refinements**

## [0.05a] - 2025-05-25

### Added
- **Keyboard Arrow Key Navigation** through current working directory
  - Left/Right arrow keys for image navigation
  - Seamless browsing through image files
  - Enhanced user experience with keyboard shortcuts

## [0.04d] - 2025-04-13

### Added
- **Keyboard Arrow Key Scrolling** functionality
  - Initial implementation of keyboard navigation
  - Improved user interaction capabilities

## [0.04c] - 2025-04-13

### Added
- **Load Last Image on Startup** feature
  - Automatic restoration of previous session
  - Improved user workflow continuity
  - Persistent image selection memory

## [0.04] - 2025-04-05

### Changed
- **Converted from tkinter to wxPython**
  - Improved GUI framework
  - Better cross-platform support
  - Enhanced user interface capabilities

## [0.10] - 2025-04-02

### Added
- **Full Image Viewer from Thumbnail**
  - Click thumbnail to view full-size image
  - Dedicated image viewing window
  - Enhanced image inspection capabilities
- **License Window under Help Menu**
  - Application licensing information
  - Legal compliance and transparency

## [0.09] - 2025-04-01

### Added
- **Export to JSON Feature**
  - Metadata export functionality
  - Data portability and backup
  - Integration with external systems
- **Clear Data option in Edit Menu**
  - Quick metadata field clearing
  - Improved workflow efficiency
  - User convenience features

## [0.08] - 2025-03-30

### Added
- **Command-line Argument Support**
  - Direct file opening from command line
  - Integration with file managers
  - Improved workflow automation
- **Status Message After Write Operations**
  - User feedback for successful operations
  - Clear indication of metadata save status
  - Enhanced user experience

## [0.07] - 2025-03-29

### Added
- **Read Existing Metadata from File for Editing**
  - Load existing IPTC metadata
  - Edit and update existing tags
  - Preserve existing metadata during editing
  - Enhanced metadata management workflow

### Enhanced
- **Improved metadata handling** with existing data preservation
- **Better user workflow** for editing existing metadata

## [0.02] - 2023-07-02

### Added
- **No-backup Option**
  - Direct file modification without backup creation
  - Streamlined writing process
  - User control over backup behavior

## [0.01] - 2023-07-01

### Added
- **Initial Release** of Tag Writer
- **GUI Interface** for IPTC metadata entry
- **Support for TIF and JPG Images**
- **Directory-based File Selection**
- **Free-form Metadata Tagging**
- **IPTC Standard Compliance**
- **Core Metadata Fields**:
  - Headline
  - Caption/Abstract
  - Credit
  - Object Name
  - Writer/Editor
  - By-line
  - Source
  - Date Created
  - Copyright Notice

### Technical
- **Initial implementation** using Python GUI libraries
- **IPTC metadata writing** capabilities
- **Image file handling** for common formats
- **Directory navigation** and file selection

---

## Version History Summary

- **v0.07k**: Fixed keyboard focus in metadata text fields for proper arrow key handling
- **v0.07j**: Fixed keyboard focus in Rename File dialog to properly handle arrow keys
- **v0.07i**: Added Refresh feature (F5 key and View menu) to reload current image and metadata
- **v0.07h**: Fixed Windows console window flashing during image loading operations
- **v0.07g**: Added Recent Directories feature and GitHub Dark theme
- **v0.07f**: Arrow key navigation, automatic zoom reset, enhanced keyboard shortcuts
- **v0.07e**: Comprehensive theme system with 7 professional themes
- **v0.07d**: Image navigation in full image window with keyboard shortcuts
- **v0.07c**: Full image window improvements (maximize/minimize, scroll bars)
- **v0.07b**: Fixed resolution detection using EXIF metadata
- **v0.07a**: Major conversion from wxPython to PyQt6 framework
- **v0.06b**: Fixed caption abstract text box editor bugs
- **v0.06a**: Added view/list all tags menu functionality
- **v0.05d**: Expanded caption abstract field to 1000 characters
- **v0.05a**: Added keyboard arrow key navigation through directories
- **v0.04d**: Initial keyboard arrow key scrolling
- **v0.04c**: Load last image on startup feature
- **v0.04**: Converted from tkinter to wxPython
- **v0.10**: Full image viewer and license window
- **v0.09**: JSON export and clear data functionality
- **v0.08**: Command-line support and status messages
- **v0.07**: Read existing metadata for editing
- **v0.02**: No-backup option
- **v0.01**: Initial release with core IPTC metadata functionality

## Future Roadmap

### Planned Features
- Enhanced metadata field support for additional IPTC fields
- Batch processing capabilities for multiple files
- Additional image format support (PNG, BMP, etc.)
- Custom metadata templates for common use cases
- Metadata validation and quality checks
- Integration with online metadata databases
- Advanced search and filtering capabilities
- Metadata synchronization between similar images

### Potential Enhancements
- Plugin system for custom metadata fields
- Workflow automation and scripting support
- Cloud storage integration
- Collaborative metadata editing
- Advanced image preview and editing tools
- Metadata analytics and reporting
- Export to various metadata standards
- Integration with digital asset management systems

