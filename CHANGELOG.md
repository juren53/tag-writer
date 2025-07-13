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

## [0.07z] - 2025-07-13 06:28:10

### Fixed
- **View All Tags Dialog** - Made the dialog read-only to prevent accidental metadata modification
  - Added `QTableWidget.EditTrigger.NoEditTriggers` to disable editing in the metadata table
  - Prevents users from accidentally modifying metadata values in the View All Tags dialog
  - Maintains the dialog's purpose as a read-only metadata viewer
  - Preserved all existing functionality including search, filtering, and column resizing

### Technical
- Modified View All Tags table configuration in `on_view_all_tags()` method
- Added `table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)` to disable editing
- Enhanced user experience by preventing unintended metadata modifications
- Maintained full table functionality while removing edit capability

## [0.07y] - 2025-07-13 01:41:00

### Enhanced
- **Caption/Abstract Field Improvements** - Enhanced Caption/Abstract text box to automatically fill available space
  - Removed fixed height constraint (was 100px max) to allow dynamic expansion
  - Added minimum height of 80px for consistent usability
  - Implemented expanding size policy to fill available vertical space in metadata panel
  - Caption/Abstract field now grows and shrinks with window resizing for optimal text entry space
  - Maintained original position between Headline and Credit fields
  - Preserved all existing functionality including character counter and validation

- **Metadata Panel Visual Organization** - Added horizontal separator line for better field grouping
  - Added horizontal line separator between Copyright Notice and Additional Info fields
  - Improved visual organization and scanning of metadata form
  - Subtle sunken line style with gray color (#888888) and proper spacing (5px margins)
  - Better separation between primary metadata fields and auxiliary information

### Technical
- Modified Caption/Abstract container with `QSizePolicy.Policy.Expanding` for vertical growth
- Updated scroll area layout with stretch factor to accommodate expanding caption field
- Added `QFrame` separator with `HLine` shape and `Shadow.Sunken` styling
- Enhanced form layout organization while maintaining all existing field functionality
- Improved metadata panel layout efficiency and user experience

## [0.07x] - 2025-07-11 19:16:02

### Enhanced
- **View All Tags Dialog Improvements** - Enhanced user experience and keyboard accessibility
  - Increased Tag column width by 100% (from ~200px to 400px) for better readability of long metadata tag names
  - Tag column now uses Interactive resize mode allowing users to adjust width as needed
  - Value column stretches to fill remaining space for optimal table layout
  - Added Ctrl+T keyboard shortcut for quick access to 'View All Tags' dialog
  - Improved metadata tag visibility without horizontal scrolling or truncation
  - Better workflow efficiency with keyboard shortcut integration

### Technical
- Modified View All Tags table configuration in `on_view_all_tags()` method
- Updated Tag column (index 0) to use `QHeaderView.ResizeMode.Interactive` with 400px initial width
- Value column (index 1) maintains `QHeaderView.ResizeMode.Stretch` for space efficiency
- Added keyboard shortcut assignment `tags_action.setShortcut("Ctrl+T")` in View menu
- Enhanced table usability while maintaining full-screen dialog functionality

## [0.07w] - 2025-07-05 19:37:18

### Added
- **ExifTool Availability Check** - Application now checks for ExifTool at startup
  - Automatic detection of ExifTool installation and accessibility
  - Clear error dialog with installation instructions when ExifTool is missing
  - Installation guidance for Windows, Linux, and macOS platforms
  - Success status shown in status bar when ExifTool is available
  - Prevents metadata operations from failing silently due to missing ExifTool
  - Helpful troubleshooting for users who have accidentally moved or deleted ExifTool

### Enhanced
- **AppImage Build Artifacts Management** - Improved .gitignore to prevent accidental commits
  - Added *.AppImage, appimagetool, and squashfs-root/ to .gitignore
  - Prevents accidental staging of large build artifacts (3,780+ files)
  - Cleaner repository management and reduced commit sizes
  - Better development workflow for AppImage builds

### Technical
- Added `check_exiftool_availability()` function with comprehensive error handling
- Implemented `show_exiftool_error_dialog()` with platform-specific installation instructions
- Added `show_exiftool_success_status()` for non-intrusive success feedback
- Enhanced startup sequence in `main()` function to include ExifTool validation
- Updated .gitignore with AppImage build artifact patterns
- FileNotFoundError and general exception handling for ExifTool detection
- Cross-platform ExifTool executable detection and version reporting

## [0.07v] - 2025-07-03 17:23:00

### Fixed
- **16-bit TIFF Image Support** - Resolved display issues with 16-bit grayscale TIFF images
  - Added automatic conversion from 16-bit (`I;16`, `I;16B`) to 8-bit (`L`) for display compatibility
  - Fixed NumPy 2.0 compatibility issue by replacing deprecated `array.ptp()` with `np.ptp()`
  - Implemented proper normalization algorithm to preserve image quality during conversion
  - Added division-by-zero protection for edge cases with uniform pixel values
  - Enhanced `load_image()` function with robust 16-bit image mode detection
  - Maintains original 16-bit data integrity for metadata operations while enabling display

### Enhanced
- **Image Loading Robustness** - Improved error handling and compatibility
  - Better support for various TIFF image modes and bit depths
  - Seamless handling of both 8-bit and 16-bit images in the same workflow
  - Preserved all existing functionality for standard image formats
  - No performance impact on non-16-bit image processing

### Technical
- Updated `load_image()` function with 16-bit to 8-bit conversion logic
- Added NumPy array normalization using `np.ptp()` for peak-to-peak calculations
- Implemented proper image mode detection for `'I;16'` and `'I;16B'` formats
- Enhanced error handling with edge case protection (zero pixel value range)
- Maintained backward compatibility with existing image processing pipeline

## [0.07u] - 2025-07-02 18:14:36

### Enhanced
- **Image Information Table** - Added professionally formatted metadata table with Color Space Data and Bits Per Sample fields
  - Replaced individual labels with neatly organized HTML table layout
  - Added Color Space Data field showing image color components (RGB, Grayscale, CMYK, etc.)
  - Added Bits Per Sample field displaying color depth information
  - Optimized table layout with proper spacing and alignment for better readability
  - Swapped order of "Dimension" and "File Size" columns for improved visual flow
  - Professional appearance with consistent margins and padding
  - Uses existing metadata reading approach for accurate color space and bits per sample extraction

### Added
- **Help Tooltips for Metadata Fields** - Added informative tooltips to key metadata labels
  - By-line: "Photographer"
  - By-line Title: "Photographer's organization"
  - Caption/Abstract: "Description"
  - Headline: "Title"
  - Object Name: "Unique Identifier / Accession Number"
  - Tooltips appear on hover with 10-second display duration
  - Enhanced responsiveness with mouse tracking enabled
  - Consistent tooltip styling across all metadata fields

### Technical
- Enhanced ImageViewer class with `extract_color_space_bits_per_sample()` method
- Implemented HTML table layout for image metadata display in `setup_ui()` and `load_image()` methods
- Updated metadata field extraction to use correct 'File:' prefixed keys for color components and bits per sample
- Improved table formatting with optimized column ordering and professional styling
- Integrated new metadata fields with existing exiftool JSON output processing
- Enhanced metadata label creation with explicit QLabel objects
- Implemented comprehensive tooltip settings (duration, mouse tracking, always show)
- Added tooltip functionality to all major metadata input fields
- Improved UI responsiveness with optimized tooltip timing

## [0.07t] - 2025-06-28 15:16:16

### Enhanced
- **DateModified Field Enhancement** - Improved date handling fallback system
  - Added ICC_Profile:ProfileDateTime as fallback for ModifyDate
  - Implemented proper date field priority order:
    1. EXIF:ModifyDate
    2. EXIF:FileModifyDate
    3. XMP:ModifyDate
    4. ICC_Profile:ProfileDateTime
  - Better support for files with missing ModifyDate but available ProfileDateTime

### Technical
- Enhanced date field fallback logic in MetadataManager
- Improved date field logging for better debugging
- Updated field mappings to include ICC_Profile:ProfileDateTime

## [0.07s] - 2025-06-28 12:19:27

### Enhanced
- **Navigation Button Improvements** - Enhanced visibility and usability
  - Added larger, clearer arrow symbols for better visibility
  - Implemented gradient backgrounds for improved visual depth
  - Increased padding and contrast for better readability
  - Added consistent button styling across toolbar and image viewer
  - Used uppercase text labels for enhanced legibility

### Technical
- Updated button styling with modern CSS gradients
- Standardized navigation button appearance across application
- Optimized button dimensions and spacing

## [0.07r] - 2025-06-28 07:41:24

### Enhanced
- **Status Bar Improvements** - Optimized status bar layout and information display
  - Removed redundant filename from status bar while keeping path
  - Moved 'Loaded {filename}' message next to the path for better readability
  - Streamlined status information presentation

- **Recent Directories Menu** - Improved directory path display in menu
  - Changed from showing only directory names to showing full paths
  - Better context and clarity when selecting from recent directories

- **Help Menu Enhancement** - Improved keyboard shortcuts documentation access
  - Added GitHub URL fallback for keyboard shortcuts documentation
  - Consistent behavior with User Guide and Glossary documentation
  - Better accessibility to documentation whether local or remote

### Technical
- Enhanced status bar layout and text display logic
- Updated Recent Directories menu to display full directory paths
- Implemented keyboard shortcuts documentation fallback system
- Improved help menu documentation access consistency

## [0.07q] - 2025-06-26 20:55:49

### Enhanced
- **Status Bar Improvements** - Optimized status bar layout and information display
  - Removed redundant filename from status bar while keeping path
  - Moved 'Loaded {filename}' message next to the path for better readability
  - Streamlined status information presentation

- **Recent Directories Menu** - Improved directory path display in menu
  - Changed from showing only directory names to showing full paths
  - Better context and clarity when selecting from recent directories

- **Help Menu Enhancement** - Improved keyboard shortcuts documentation access
  - Added GitHub URL fallback for keyboard shortcuts documentation
  - Consistent behavior with User Guide and Glossary documentation
  - Better accessibility to documentation whether local or remote

### Technical
- Enhanced status bar layout and text display logic
- Updated Recent Directories menu to display full directory paths
- Implemented keyboard shortcuts documentation fallback system
- Improved help menu documentation access consistency

## [0.07q] - 2025-06-26 20:55:49

### Enhanced
- **Full Image Pop-up Window Layout** - Improved control button organization
  - Arranged control buttons vertically on the right side of the window
  - Added clear visual separation between button groups with horizontal lines
  - Improved button grouping for better usability and appearance
  - Fixed panel width to 100px for consistent layout
  - Better organization of image display and controls

## [0.07p] - 2025-06-24 02:01:44

### Added
- **Window Position and Size Memory** - Application now remembers window geometry between sessions
  - Automatically saves window position, size, and maximized state on close
  - Restores exact window layout on next startup
  - Screen bounds validation ensures window remains visible
  - Minimum size enforcement prevents unusable tiny windows
  - Fallback to default size (1000x600) if restoration fails
  - Configuration stored in `~/.tag_writer_config.json` with other settings

### Enhanced
- **Full Image Viewer Control Bar** - Optimized button sizes for better screen space usage
  - Navigation buttons: "◀ Previous" → "◀ Prev" (60px max width)
  - Navigation buttons: "Next ▶" kept but limited to 60px max width
  - Reset button: "Reset Zoom" → "Reset" (50px max width)
  - Fit button: "Fit to Window" → "Fit" (40px max width)
  - Zoom buttons: "-" and "+" reduced from 30px to 25x25px square buttons
  - Prevents control bar from extending beyond screen boundaries
  - Ensures Exit button in upper right corner remains visible and accessible

- **Scroll Bar Visibility** - Improved scroll bar styling for better visibility in all themes
  - Enhanced scroll bar colors with theme-appropriate contrasting borders
  - Hover effects for better visual feedback and interactivity
  - Pressed states with enhanced borders for clear user interaction
  - Scroll buttons with proper arrow indicators using theme text colors
  - Both vertical and horizontal scroll bars with consistent styling
  - Significantly improved visibility in Dark theme and other color schemes
  - Transparent page areas to avoid visual clutter

### Fixed
- **Full Image Pop-up Window Layout** - Resolved window overflow issues
  - Control bar buttons now properly fit within screen boundaries
  - Compact button design prevents right edge from running off screen
  - All navigation and zoom controls remain accessible
  - Exit button always visible in upper right corner

### Technical
- Added `window_geometry` and `window_maximized` attributes to Config class
- Implemented `save_window_geometry()` and `restore_window_geometry()` methods
- Enhanced configuration persistence to include window state data
- Integrated window geometry saving in cleanup process before application close
- Added comprehensive scroll bar styling to ThemeManager stylesheet generation
- Updated Full Image Viewer button sizing with `setMaximumWidth()` and `setFixedSize()` constraints
- Enhanced scroll bar CSS with hover states, arrow indicators, and theme-consistent colors

## [0.07o] - 2025-06-23 00:00:00

### Enhanced
- **Set Today's Date Menu Function** - Improved functionality for date management
  - 'Set Today's Date' in Edit menu now targets the Date Modified field instead of Date Created
  - More logical workflow: Date Created represents original capture date, Date Modified represents processing date
  - Maintains YYYY:MM:DD format compatible with IPTC standards
  - Proper integration with EXIF:ModifyDate metadata field
  - Enhanced user experience with contextually appropriate date setting

### Changed
- **Menu Action Behavior** - 'Set Today's Date' function redirected to Date Modified field
  - Previous behavior: Set Date Created field to today's date
  - New behavior: Set Date Modified field to today's date
  - Updated logging and status messages to reflect the change
  - Better semantic alignment with typical metadata workflow

### Technical
- Modified `set_today_date()` method in MetadataPanel class
- Updated method documentation and logging messages
- Maintained backward compatibility with existing date formatting
- Enhanced user feedback through status bar updates

## [0.07n] - 2025-06-22/23

### Added
- **Additional Info Field** - New metadata field for contact information and URLs
  - Located under Copyright Notice in the main UI
  - Uses IPTC:Contact metadata field for storage
  - Fully integrated with all existing functionality (save/load, import/export, clear fields)
  - Supports keyboard navigation and focus handling
  - Perfect for storing URLs, contact information, or additional references

- **Date Modified Field** - New metadata field for tracking image modification dates
  - Reads from EXIF:ModifyDate, EXIF:FileModifyDate, and XMP:ModifyDate
  - Positioned on same line as Writer/Editor field for efficient space usage
  - Automatically populated from image metadata when available
  - Fully integrated with all metadata operations

### Enhanced
- **Optimized UI Layout** - Improved screen real estate utilization
  - Date Created and Source fields now share the same horizontal line
  - Date Modified and Writer/Editor fields positioned together at bottom
  - Proper label alignment with consistent spacing and professional appearance
  - Compact field widths for date fields (120px) with labels properly sized
  - More efficient use of vertical space in metadata panel

- **Help Menu Fallback System** - Improved Help and Glossary menu functionality
  - User Guide and Glossary now check for local files first
  - Automatically falls back to GitHub URLs when local documentation not found
  - Local files displayed in formatted dialog windows when available
  - GitHub URLs: User Guide and Glossary open in default web browser as fallback
  - Seamless experience whether documentation is local or remote
  - Enhanced error handling with informative user feedback

### Technical
- Added Contact field mapping to MetadataManager with IPTC:Contact and XMP:Contact support
- Added DateModified field mapping with EXIF:ModifyDate, EXIF:FileModifyDate, XMP:ModifyDate support
- Implemented horizontal layout containers for paired fields (Date Created+Source, Date Modified+Writer/Editor)
- Enhanced UI layout with proper field ordering and keyboard focus integration
- Updated all metadata operations to include new Additional Info and Date Modified fields
- Implemented fallback URL system for Help menu items with webbrowser module integration
- Improved error handling for documentation access with graceful degradation
- Enhanced form layout with QHBoxLayout for space-efficient field pairing

## [0.07m] - 2025-06-19

### Added
- **Glossary in Help Menu** - Added quick access to terminology reference
  - New Help menu option for the Glossary
  - Links to comprehensive Docs/glossary.md file
  - Provides definitions for IPTC, metadata, and technical terms
  - Displayed in scrollable, searchable window

### Changed
- **Improved Help Menu Organization** - Reorganized the Help menu for better usability
  - Reordered menu items: Help, User Guide, Glossary, Keyboard Shortcuts, About
  - Removed separate License menu item
  - Added License information to About dialog
  - Improved User Guide display with proper markdown rendering

## [0.07l] - 2025-06-19

### Added
- **Keyboard Shortcuts Documentation** - Added comprehensive keyboard shortcuts reference
  - New KeyBoard-ShortCuts.md file with detailed shortcut listings
  - Added "Keyboard Shortcuts" entry in Help menu for easy access
  - Documentation includes navigation, editing, and viewer shortcuts
  - Improved user experience with better keyboard control discovery
- **Copy FQFN to Clipboard** - Added ability to copy the Fully Qualified File Name to the clipboard
  - Available in the Edit menu
  - Provides easy access to the full file path for sharing or referencing
  - Confirmation message appears in status bar
  - Useful for integrating with other applications
- **Open in Default Editor** - Added ability to open images in system's default editor
  - Available via Ctrl+Shift+E keyboard shortcut
  - Available in the Edit menu as "Open in Default Editor"
  - Available in the image thumbnail context menu (right-click)
  - Warning dialog explains potential metadata changes
  - Improves workflow by allowing external image editing

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

- **v0.07w**: Added ExifTool availability check at startup and improved .gitignore for AppImage builds
- **v0.07v**: Fixed 16-bit TIFF image display support
- **v0.07u**: Enhanced metadata field tooltips and improved image information table
- **v0.07m**: Added Glossary to Help menu and improved Help menu organization
- **v0.07l**: Added keyboard shortcuts documentation and improved keyboard control discovery
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

