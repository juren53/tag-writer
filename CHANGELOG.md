# Tag-writer Changelog

All notable changes to the Tag Writer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - Sat 15 Feb 2026 10:15:00 PM CST

### Changed
- **Modular Architecture** - Refactored monolithic 5,237-line `tag-writer.py` into a clean package structure under `src/tag_writer/`
  - 24 Python modules organized by responsibility (constants, config, platform, utilities, core classes, widgets, dialogs, mixins)
  - MainWindow composed from 7 mixins: MenuMixin, WindowMixin, NavigationMixin, FileOpsMixin, ThemeMixin, HelpMixin, UpdatesMixin
  - Root `tag-writer.py` reduced to thin wrapper that imports and launches the package
  - Strict dependency ordering prevents circular imports: constants → config → utilities → core classes → widgets/dialogs → mixins → main

### Added
- **Bundled ExifTool** - ExifTool binary now ships in `tools/` directory
  - 3-tier path resolution: PyInstaller frozen → `tools/exiftool.exe` → system PATH
  - Persistent ExifTool process singleton stays alive for app lifetime instead of spawning per operation
  - Faster image paging when browsing directories
- **Persistent ExifTool Process** - New `PersistentExifTool` class in `exiftool_utils.py`
  - Singleton pattern keeps ExifTool running across metadata reads/writes
  - Automatic cleanup on application shutdown via `cleanup_resources()`

### Technical
- New package structure: `src/tag_writer/` with `__init__.py` exporting all public API
- Entry point: `src/main.py` with `MainWindow` mixin composition and `main()` function
- `tag-writer.spec` updated with `pathex=['src']`, bundled ExifTool, Docs, and version checker
- Original monolithic file preserved as `tag-writer.py.bak` for reference
- Module breakdown:
  - `constants.py` — version info, image extensions, timeouts
  - `config.py` — Config class, SingleInstanceChecker, global singleton
  - `platform.py` — Windows AppUserModelID and taskbar integration
  - `exiftool_utils.py` — ExifTool path resolution, persistent process, timeout helper
  - `image_utils.py` — PIL image loading, thumbnails, zoom, pil_to_pixmap
  - `file_utils.py` — file scanning, backup, metadata reading
  - `metadata.py` — MetadataManager with IPTC/XMP/EXIF field mappings
  - `theme.py` — ThemeManager with 8 themes and stylesheet generation
  - `dialogs/` — ThemeDialog, PreferencesDialog
  - `widgets/` — MetadataPanel, ImageViewer, FullImageViewer
  - `menu.py`, `window.py`, `navigation.py`, `file_ops.py`, `theme_mixin.py`, `help.py`, `updates.py` — MainWindow mixins

## [0.1.7a] - Sun 15 Feb 2026 02:05:00 PM CST

### Added
- **Preferences Dialog** - New application preferences system
  - Added Preferences dialog accessible from Edit menu
  - "Automatically check for updates on startup" toggle option
  - Extensible design for future preference additions
  - Settings persist to configuration file

### Changed
- **Auto-update Default** - Changed default behavior for automatic update checking to OFF
  - Users now opt-in to automatic update checking via Preferences
  - No startup update check pop-ups unless explicitly enabled by user
  - Manual update checking still available via Help menu
  - Provides cleaner startup experience for users who prefer manual control

### Improved
- **Debug prints replaced with logger** - Converted remaining `print(DEBUG:...)` calls to `logger.debug()` for proper log-level control
- **Directory scanning performance** - Replaced `os.listdir()` + `os.path.isfile()` with `os.scandir()` in `get_image_files()`, avoiding extra stat calls per file
- **Path traversal protection** - File rename dialog now sanitizes input with `os.path.basename()` and rejects `.`, `..`, empty names, and null bytes
- **JPEG quality preservation on rotation** - Rotated JPEGs now save with `quality=95, subsampling=0` to prevent degradation; TIFF uses LZW compression
- **Metadata value sanitization** - New `_sanitize_value()` method strips null bytes, normalizes line endings, trims whitespace, and truncates values >2000 chars before writing to ExifTool
- **Rotation error recovery** - Metadata save failure after rotation now offers to restore from backup instead of silently failing or raising an error
- **ExifTool timeout protection** - All ExifTool calls wrapped with 30-second timeout via `concurrent.futures` to prevent application hangs on unresponsive ExifTool processes

### Technical
- Added PreferencesDialog class with Updates section
- Added QGroupBox and QCheckBox to PyQt6 imports
- Added Preferences menu item to Edit menu
- Changed auto_check_updates default from True to False
- Preferences persist to config file via save_config()
- Added `import concurrent.futures` and `EXIFTOOL_TIMEOUT = 30` constant
- Added `execute_with_timeout()` helper function
- Added `MetadataManager._sanitize_value()` static method

## [0.1.7] - Sun 11 Jan 2026 08:21:25 AM CST

### Enhanced
- **View Image Pane Date Display** - Improved readability with three-column layout
  - Restructured date information display to separate field name, date value, and metadata source
  - Column 1: Field name (Date Created, Date Modified, File Creation, File Modified)
  - Column 2: Date/time value in YYYY-MM-DD HH:MM:SS format
  - Column 3: Metadata source tag (IPTC:DateCreated, EXIF:ModifyDate, File System, etc.)
  - Date format standardized with dashes instead of colons for better readability
  - Metadata source displayed in italics and grey color for visual distinction
  - Includes time information when available from metadata or file system
  - Enhanced date field detection to include EXIF:DateTimeOriginal and EXIF:CreateDate
  - Automatic pairing of separate date and time fields when available
  - System dates labeled as "File System" instead of "System" for clarity

### Added
- **Credits Dialog** - Recognition of key contributors to Tag Writer
  - New Credits dialog accessible from About dialog via Credits button
  - Phil Harvey acknowledged as Father of ExifTool
  - PyQt Team credited for GUI framework libraries
  - Guido van Rossum honored as Father of Python
  - Professional formatted dialog with scrollable content
  - Thank you message to open source community
  - Enhanced About dialog converted to custom dialog with Credits button

### Technical
- Restructured `extract_date_metadata()` to return dictionaries with 'value' and 'source' keys
- Added `_format_date_value()` method to convert YYYY:MM:DD format to YYYY-MM-DD
- Updated HTML table layouts in `setup_ui()` and `load_image()` for three-column date display
- Implemented `on_credits()` method with scrollable dialog and proper parent dialog handling
- Enhanced About dialog with QDialog instead of QMessageBox for better control

## [0.1.6a] - Mon 05 Jan 2026 11:08:39 AM CST

### Added
- **Windows App User Model ID** - Enhanced Windows 11 taskbar integration
  - Set explicit App User Model ID (SynchroSoft.TagWriter.TW.0.1.6) for Windows systems
  - Improved taskbar icon display and grouping in Windows 11
  - Better application identification in Windows task switcher
  - Enhanced integration with Windows shell features

### Technical
- Implemented Windows App User Model ID registration at application startup
- Added logging for App User Model ID configuration
- Integration with single instance checker for proper Windows behavior

## [0.1.6] - Mon 05 Jan 2026 08:42:50 AM CST

### Added
- **Enhanced UI Zoom Controls** - Comprehensive keyboard and mouse wheel support
  - Added keyboard shortcuts: Ctrl++/Ctrl+Shift+= for zoom in, Ctrl+-/Ctrl+_ for zoom out
  - Added Ctrl+0 shortcut for zoom reset to 100%
  - Added Ctrl+mouse wheel support with 5% zoom steps
  - Keyboard shortcuts use 10% increments, mouse wheel uses 5% increments

- **Single Instance Enforcement** - Prevents multiple instances from running simultaneously
  - Only one instance of Tag Writer can run at a time
  - Displays informative dialog when attempting to launch additional instances
  - Uses cross-platform file locking mechanism (works on Windows, Linux, macOS)
  - Lock file automatically cleaned up on application exit
  - Prevents data conflicts and resource contention
  - Improved application stability and user experience

### Fixed
- **Desktop Icon Display** - Resolved icon visibility issues in application menus
  - Removed 4 conflicting userapp-tag-writer-*.desktop files causing display conflicts
  - Installed icon to standard XDG locations (~/.local/share/icons/hicolor/256x256/apps/)
  - Enhanced .desktop file with proper Version, GenericName, and Keywords fields
  - Added comprehensive MIME type associations for image file handling
  - Added Photography category and improved Categories metadata
  - Icon now properly displays in desktop environment application menus
  - Desktop database and icon cache updated for immediate recognition

### Changed
- **UI Zoom Persistence** - Removed startup reset, user zoom preference now persists across sessions
  - UI zoom factor is now loaded from saved configuration
  - Users no longer need to manually adjust zoom each application restart
  - Forced 100% reset on startup removed from Config class

### Technical
- Enhanced eventFilter to support Ctrl+mouse wheel zoom detection
- Added QPropertyAnimation for smooth zoom transitions with InOutQuad easing
- Updated zoom_ui() method to support both instant and animated zoom changes
- Multiple keyboard shortcuts supported for international keyboard layouts
- Implemented SingleInstanceChecker class with cross-platform file locking
- Added fcntl-based locking for Unix/Linux and msvcrt-based locking for Windows
- Lock file stored in system temp directory with automatic cleanup on exit
- Comprehensive exception handling for lock acquisition and release

## [2.0.0] - Sat 04 Jan 2026 06:39:47 PM CST

### Changed
- **Major Release - GitHub Release Management Complete** - Professional release infrastructure implemented
  - **All releases successfully published** to GitHub with comprehensive release notes
  - **Version checking system now functional** - users can properly check for updates
  - **Professional release history established** with v2.0.0, v0.1.5, v0.1.4, v0.1.3, v0.1.2
  - **API integration working** - TagWriter can now fetch version information from GitHub releases
  - **Download functionality operational** - users can download different versions directly
  - **No more "no releases" message** - repository now has proper release management

### Added
- **Professional Release Management System** - Complete GitHub release workflow
  - **Version 2.0.0** - Major release with comprehensive changes and optimizations
  - **Version 0.1.5** - System optimizations and performance improvements  
  - **Version 0.1.4** - Bug fixes and documentation integration
  - **Version 0.1.3** - UI/UX improvements and help menu enhancements
  - **Version 0.1.2** - Initial release with basic features
  - **Comprehensive release notes** for each version with detailed changelog
  - **Proper tagging** and version management following semantic versioning

### Technical
- **GitHub API Integration** - Version checking system now properly connected to GitHub releases
- **Release Infrastructure** - Professional release management workflow established
- **Version Control** - Semantic versioning properly implemented
- **Download System** - Users can now download releases directly from GitHub
- **Status Resolution** - Repository moved from "no releases" to "proper releases" status

## [0.1.5] - Sat 04 Jan 2026 02:24:22 PM CST

### Changed
- **Image Viewer Panel Layout Optimization** - Improved space efficiency with vertical layout
  - Removed Photometric Interpretation and Bits Per Sample fields (no longer needed)
  - Reconfigured from 2-column horizontal layout to single-column vertical layout
  - Added QScrollArea with automatic vertical scrolling when needed
  - Optimized spacing and margins for compact display (10px margins, 3px row spacing)
  - Improved readability with better organization of image metadata
  - Consistent user experience with Metadata Panel scrolling behavior
  - More efficient use of available space in Image Viewer panel

- **Update Message Simplification** - Commented out technical explanation in "No Releases Available" message
  - Removed "The update checking system is working correctly, but no official releases have been published"
  - Users now see more concise message when repository has no releases
  - Maintains friendly user experience while reducing technical jargon

### Added
- **Documentation Accessibility** - Enhanced changelog accessibility through Help menu
  - Centralized version history access with offline/online capability
  - Professional modal dialog with scrollable content and proper encoding
  - Comprehensive error handling for file permission and network issues
  - Consistent UI patterns with existing Help menu items

### Technical
- Enhanced ImageViewer class with vertical table layout using HTML formatting
- Implemented QScrollArea for metadata table with horizontal scrollbar disabled
- Removed extract_photometric_interpretation_bits_per_sample() method call
- Streamlined metadata display to 8 essential fields (file size, dimension, resolution, pixel count, dates)

## [0.1.4] - Wed 01 Jan 2026 06:12:30 PM CST

### Added
- **Documentation Accessibility** - Enhanced changelog accessibility through Help menu
  - Centralized version history access with offline/online capability
  - Professional modal dialog with scrollable content and proper encoding
  - Comprehensive error handling for file permission and network issues
  - Consistent UI patterns with existing Help menu items

### Changed
- **Help Menu Order** - Changelog item positioned logically in documentation flow
- **File Priority** - Local CHANGELOG.md prioritized over GitHub fallback
- **Dialog Sizing** - Optimized for changelog readability (800x600 pixels)

## [0.1.3] - Wed 01 Jan 2026 05:14:37 PM CST

### Added
- **Help Menu Changelog Link** - Added "&Changelog" menu item
  - Opens local CHANGELOG.md when available (standard and AppImage locations)
  - Falls back to GitHub repository when local file not found
  - Modal dialog with scrollable text area and proper UTF-8 encoding
  - Comprehensive error handling for file access and network issues
  - Follows established Help menu UI patterns and naming conventions

## [0.1.2] - Wed 31 Dec 2025 11:32:48 PM CST

### Changed
- **PyInstaller Build Configuration** - Switched to single-file executable mode
  - Modified tag-writer.spec from COLLECT mode to onefile mode
  - Bundles all dependencies into a single executable file
  - Changed application icon from ICON_tw.ico to ICON_tw.png format
  - Simplified distribution with single executable instead of directory structure
  - Improved portability and ease of deployment

### Added
- **GitHub Version Checking System** - Integrated comprehensive update checking functionality
  - Added automatic startup checks with configurable frequency (default: 24 hours)
  - Added manual "Check for Updates" menu item in Help menu
  - Implemented non-blocking version checks using PyQt6 threading
  - Added rich update dialogs with release notes and download options
  - Added version skipping functionality with persistent user preferences
  - Implemented semantic version comparison supporting pre-release versions
  - Added comprehensive error handling for network and API issues
  - Added user preferences for update checking behavior
  - Enhanced error messages for repositories without releases
  - Integrated proven version checker module from system-monitor project

## [0.1.0] - Mon 15 Dec 2025 04:50:46 AM CST

### Fixed
- **UTF-8 Encoding for Metadata Display** - Resolved mojibake issues with special characters in IPTC metadata
  - Added `encoding='utf-8'` parameter to ExifTool instances in `create_exiftool_instance()` function
  - Fixed display of special characters (ñ, é, etc.) in IPTC:Headline and IPTC:Caption-Abstract fields
  - Application now correctly interprets `IPTC:CodedCharacterSet=UTF8` from TIFF files
  - Eliminates mojibake display (e.g., "NiÃ±os HÃ©roes" now correctly displays as "Niños Héroes")
  - Matches UTF-8 encoding implementation from HSTL Photo Framework
  - Affects both WindowsExifTool and standard ExifTool instances for cross-platform consistency

### Changed
- **Version Update** - Bumped version from 0.07z to 0.1.0
  - Updated version display in main window status bar
  - Updated version display in Help > About dialog
  - Timestamp updated to 2025-12-15 04:40

### Technical
- Modified `create_exiftool_instance()` at lines 312 and 315
- Changed `WindowsExifTool()` to `WindowsExifTool(encoding='utf-8')`
- Changed `exiftool.ExifTool()` to `exiftool.ExifTool(encoding='utf-8')`
- Ensures consistent UTF-8 handling across all metadata read/write operations

### Enhanced
- **Photometric Interpretation Display** - Improved readability of color space information (2025-07-28 18:25:14)
  - Added human-readable photometric interpretation values in image metadata table
  - Converts numeric EXIF codes (0,1,2,etc.) to descriptive text (WhiteIsZero, BlackIsZero, RGB, etc.)
  - Based on official TIFF/EXIF specification mapping for photometric interpretation values
  - Enhanced user experience by displaying meaningful text instead of cryptic numeric codes
  - Improved accessibility and understanding of technical image metadata
  - Better debugging and analysis capabilities for advanced users

### Added

- **Command-line File Argument Support** - Application now accepts image file paths as command-line arguments (2025-07-28 15:42:27)
  - Enhanced `main()` function to handle single file path argument on startup
  - Automatic validation to ensure argument is a valid image file (by existence, type, and supported extensions)
  - Supported extensions: .jpg, .jpeg, .png, .gif, .tif, .tiff, .bmp
  - If valid image file provided as argument, it will be opened automatically on startup
  - Enables "Open with tag-writer" functionality from OS file managers
  - Falls back to loading last used file if no command-line argument provided (maintains existing behavior)
  - Usage: `python3 tag-writer.py /path/to/image.tiff`
  - Improved integration with operating system file associations

- **EXIF Photometric Interpretation Documentation** - Comprehensive technical documentation resources (2025-07-29 08:45:18)
  - Added `INFO_EXIF Photometric Interpretation.md` with detailed explanations of photometric interpretation values
  - Added `INFO_EXIF Photometric Interpretation.txt` with technical reference details
  - Included official TIFF 6.0 specification PDF (`tiff6.pdf`) for complete technical reference
  - Documentation covers different photometric interpretation values and their meanings
  - Enhanced user understanding of color space and image technical details
  - Fixed broken links and improved documentation accessibility
  - Valuable resource for photographers and technical users

- **AppImage Packaging Infrastructure** - Complete Linux distribution packaging system (2025-07-29 07:30:45)
  - Added complete `TagWriter.AppDir` structure for AppImage builds
  - Includes desktop entry files, application icons, and executable binaries
  - Professional application packaging for Linux distribution
  - Self-contained portable application format
  - Enhanced cross-platform deployment capabilities
  - Simplified installation process for Linux users

- **Python Dependencies Management** - Added `requirements.txt` for better development workflow (2025-07-29 06:55:12)
  - Explicit Python package dependencies specification
  - Improved development environment setup
  - Enhanced reproducible builds and deployments
  - Better dependency management for contributors and users

- **Theme Issues**  Fixed default Light theme styling for form labels and input fields  ()Wed Jul 23 2025 10:22:10)  
  - Enhanced label styling with proper text color inheritance and transparent backgrounds
  - Added focus states for input fields with visual feedback (border changes on focus)
  - Improved widget container styling with proper background and text color inheritance
  - Added form layout specific styling to ensure proper theming
  - Fixed scroll area background colors and child widget styling
  - Added proper theming for frame elements
  - Resolved issue with dark backgrounds behind metadata fields making labels unreadable
  - Default Light theme now uses softer, more readable color palette throughout


## [0.07z] - Sun 13 Jul 2025 06:31:30 AM CDT

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

## [0.07y] - Sat 12 Jul 2025 08:46:28 PM CDT

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
  - Addition of a search bar to filter tags and values
  - Keyboard shortcut (Ctrl+F) to focus on the search field

### Technical
- Modified View All Tags table configuration in `on_view_all_tags()` method
- Updated Tag column (index 0) to use `QHeaderView.ResizeMode.Interactive` with 400px initial width
- Value column (index 1) maintains `QHeaderView.ResizeMode.Stretch` for space efficiency
- Added keyboard shortcut assignment `tags_action.setShortcut("Ctrl+T")` in View menu
- Enhanced table usability while maintaining full-screen dialog functionality

## [0.07w] - Sat 05 Jul 2025 07:58:08 PM CDT

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

## [0.07v] - Thu 03 Jul 2025 05:30:17 PM CDT

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

- **Full Image Pop-up Window Layout** - Improved control button organization
  - Arranged control buttons vertically on the right side of the window
  - Added clear visual separation between button groups with horizontal lines
  - Improved button grouping for better usability and appearance
  - Fixed panel width to 100px for consistent layout
  - Better organization of image display and controls

### Technical
- Enhanced status bar layout and text display logic
- Updated Recent Directories menu to display full directory paths
- Implemented keyboard shortcuts documentation fallback system
- Improved help menu documentation access consistency

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

### Recent Releases
- **v0.1.7a** - Sun 11 Jan 2026 02:32:33 PM CST: Added Preferences dialog with auto-update toggle, changed default auto-update behavior to OFF
- **v0.1.7** - Sun 11 Jan 2026 08:21:25 AM CST: Enhanced date display with three-column layout, added Credits dialog with acknowledgments for ExifTool, PyQt, and Python creators
- **v0.1.6a** - Mon 05 Jan 2026 11:08:39 AM CST: Windows App User Model ID for enhanced Windows 11 taskbar integration
- **v0.1.6** - Mon 05 Jan 2026 08:42:50 AM CST: Single instance enforcement, desktop icon fixes, enhanced UI zoom controls with persistence
- **v2.0.0** - Sat 04 Jan 2026 06:39:47 PM CST: **MAJOR RELEASE** - Complete GitHub release management implementation, version checking system functional, professional release infrastructure
- **v0.1.5** - Sat 04 Jan 2026 02:24:22 PM CST: Image Viewer panel layout optimization, improved space efficiency with vertical layout
- **v0.1.4** - Wed 01 Jan 2026 06:12:30 PM CST: Enhanced changelog accessibility through Help menu, improved documentation integration
- **v0.1.3** - Wed 01 Jan 2026 05:14:37 PM CST: Added Help Menu Changelog link with local/GitHub fallback functionality
- **v0.1.2** - Wed 31 Dec 2025 11:32:48 PM CST: PyInstaller build configuration switched to single-file executable mode

### Historical Releases
- **v0.07z** - Sun 13 Jul 2025 06:31:30 AM CDT: Added ExifTool availability check at startup and improved .gitignore for AppImage builds
- **v0.07y** - Sat 12 Jul 2025 08:46:28 PM CDT: Enhanced Caption/Abstract field and metadata panel organization  
- **v0.07w** - Sat 05 Jul 2025 07:58:08 PM CDT: Added ExifTool availability check at startup and improved .gitignore for AppImage builds
- **v0.07v** - Thu 03 Jul 2025 05:30:17 PM CDT: Fixed 16-bit TIFF image display support
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
- **v0.1.0** - Mon 15 Dec 2025 04:50:46 AM CST: Fixed UTF-8 mojibake in metadata display
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

