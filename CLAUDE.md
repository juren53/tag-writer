# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tag Writer is a PyQt6 desktop application for viewing and editing IPTC/XMP/EXIF metadata in image files (JPG, TIFF, PNG). It uses ExifTool for metadata operations and Pillow for image handling. Current version: v0.2.1.

## Development Commands

### Running the Application
```bash
python tag-writer.py

# Open a specific image
python tag-writer.py path/to/image.jpg
```

### Building Executable
```bash
pyinstaller tag-writer.spec --noconfirm
# Output: dist/tag-writer.exe
```

### Dependencies
```bash
pip install -r requirements.txt
# PyExifTool, PyQt6, Pillow
```

## Critical Project Rules

### Timezone Convention
**ALL timestamps MUST use Central Time USA (CST/CDT), NEVER UTC.**

This applies to:
- Changelog entries
- Version labels (APP_TIMESTAMP in src/tag_writer/constants.py)
- Documentation timestamps

### Version Numbering
- Production releases: `v0.X.Y` (e.g., v0.2.0)
- Point releases/patches: `v0.X.Ya`, `v0.X.Yb` (e.g., v0.1.7a)
- Update version in: `src/tag_writer/constants.py` (APP_VERSION, APP_TIMESTAMP, APP_USER_MODEL_ID), `tag-writer.py` (header comment), `tag-writer.spec` (version comment), `README.md`, `CHANGELOG.md`

## Architecture

### Modular Package Structure (v0.2.1)

The application uses a mixin-based architecture under `src/tag_writer/` (24 modules). Root `tag-writer.py` is a thin wrapper that adds `src/` to the path and calls `main()`.

```python
# MainWindow composition in src/main.py
class MainWindow(MenuMixin, WindowMixin, NavigationMixin, FileOpsMixin,
                 ThemeMixin, HelpMixin, UpdatesMixin, QMainWindow):
```

### Module Dependency Flow
constants → config → utilities → core classes → widgets/dialogs → mixins → main

**Do not introduce circular imports.** Follow this strict ordering.

### Key Modules

| Module | Purpose |
|--------|---------|
| `constants.py` | APP_VERSION, APP_TIMESTAMP, IMAGE_EXTENSIONS, EXIFTOOL_TIMEOUT |
| `config.py` | Config singleton, SingleInstanceChecker (file locking) |
| `platform.py` | Windows AppUserModelID, taskbar icon |
| `exiftool_utils.py` | get_exiftool_path() (3-tier), PersistentExifTool singleton, execute_with_timeout() |
| `metadata.py` | MetadataManager — 11 IPTC/XMP/EXIF field mappings, load/save/export/import |
| `theme.py` | ThemeManager — 8 themes, generate_stylesheet() |
| `menu.py` | MenuMixin — create_menu_bar(), create_toolbar() |
| `window.py` | WindowMixin — eventFilter, geometry save/restore, closeEvent, cleanup_resources() |
| `navigation.py` | NavigationMixin — open, prev/next (looping), load_file, recent files/dirs |
| `file_ops.py` | FileOpsMixin — save, export, import, rename, rotate, view all tags |
| `theme_mixin.py` | ThemeMixin — apply_theme, zoom_ui, dark mode toggle |
| `help.py` | HelpMixin — about, credits, user guide, glossary, shortcuts, changelog |
| `updates.py` | UpdatesMixin — GitHub version check, UpdateCheckThread |
| `widgets/metadata_panel.py` | MetadataPanel — form with 11 fields, char count, write button |
| `widgets/image_viewer.py` | ImageViewer — thumbnail, resolution, date metadata, context menu |
| `widgets/full_image_viewer.py` | FullImageViewer — zoom, pan, keyboard nav |
| `dialogs/theme_dialog.py` | ThemeDialog — combo, preview |
| `dialogs/preferences_dialog.py` | PreferencesDialog — auto-update toggle |

### Global Config Singleton
All modules import `config` from `tag_writer.config`. It manages:
- App state (selected_file, last_directory, recent files/dirs)
- UI state (dark_mode, current_theme, ui_zoom_factor, window_geometry)
- Update settings (auto_check_updates, skipped_versions)
- Persisted to `~/.tag_writer_config.json`

### ExifTool Integration
- Binary bundled in `tools/exiftool.exe`
- 3-tier path resolution: PyInstaller frozen → `tools/exiftool.exe` → system PATH
- PersistentExifTool singleton keeps process alive for app lifetime
- All calls use 30-second timeout via concurrent.futures
- Console window hidden on Windows (CREATE_NO_WINDOW flag)

### Mixin Pattern
Mixins access MainWindow attributes via `self.` (metadata_panel, image_viewer, status_label, etc.) set in `setup_ui()`. Cross-mixin calls work because all compose into one class at runtime.

## Directory Structure

```
tag-writer/
├── src/
│   ├── main.py                    # MainWindow + main() entry point
│   └── tag_writer/                # Package (24 modules)
│       ├── dialogs/               # ThemeDialog, PreferencesDialog
│       └── widgets/               # MetadataPanel, ImageViewer, FullImageViewer
├── tools/
│   └── exiftool.exe               # Bundled ExifTool binary
├── Docs/                          # User guide, glossary, keyboard shortcuts
├── archive/                       # Old versions
├── tag-writer.py                  # Thin wrapper launcher
├── tag-writer.spec                # PyInstaller build spec
├── github_version_checker.py      # GitHub release version checker
├── ICON_tw.ico / .png             # Application icons
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

## Common Issues

**SingleInstanceChecker blocks launch**: Delete `%TEMP%/tag-writer.lock` if app crashed without cleanup.

**ExifTool not found**: Ensure `tools/exiftool.exe` exists or exiftool is on PATH. Check with `exiftool -ver`.

**Icon not showing in PyInstaller build**: Icons must be in spec `datas` list and `_get_icon_path()` in `src/main.py` handles frozen path resolution via `sys._MEIPASS`.

**Import errors after adding modules**: Check dependency ordering. New utilities go before classes that use them. New mixins go after widgets/dialogs.
