# Tag Writer

**Version 0.2.0** | PyQt6 | Python 3

Tag Writer is a free, open-source application designed to view and edit IPTC metadata in image files (JPG and TIF formats). This tool is particularly useful when metadata cannot be pulled from an online database and needs to be entered manually.

The application provides a simple graphical user interface for editing common IPTC metadata fields, allowing photographers, archivists, and digital asset managers to properly tag their images with essential information.

![Tag Writer Main Window](Docs/Images/main-window.png)

tag-writer has been tested against the following file types:

- JPEG / JPG
- TIFF / TIF
- PNG

 IPTC tag set
 ```
           IPTC Tag Names                   HSTL PDB Labels
     - Headline                        : {title} e.g. 2018 Harry's Hop n' Hunt
     - Caption-Abstract                : {description} e.g. Easter Egg Roll at the 2018 Harry's Hop'n Hunt.<br>
     - Object Name                     : {Accession No} e.g. 2010-365
     - By-line                         : {photographer}
     - By-line Title                   : {Institutional Creator}
     - Credit                          : {Credit} Harry S. Truman Library
     - Source                          : {collection} e.g. RG 64
     - Copyright Notice                : {Restrictions} Public Domain - This item is in the public domain and can be used freely without further permission.
     - Writer-Editor                   : {archivist/editor} e.g. LAA
```

## Features

- Edit 11 IPTC/XMP/EXIF metadata fields with a form-based UI
- Image thumbnail preview with resolution and date metadata display
- Full-size image viewer with zoom, pan, and keyboard navigation
- Directory browsing with arrow key navigation between images
- 8 built-in color themes (Default Light, Warm Light, Dark, Solarized Light/Dark, High Contrast, Monokai, GitHub Dark)
- UI zoom (50%–150%) with Ctrl+/Ctrl-
- Export/import metadata as JSON
- Image rotation with metadata preservation
- Recent files and recent directories menus
- Automatic update checking via GitHub releases
- Single-instance enforcement (prevents duplicate windows)
- Bundled ExifTool with persistent process for fast image paging

## Architecture (v0.2.0)

Tag Writer uses a modular package architecture under `src/tag_writer/` with the MainWindow composed from 7 mixins:

```
tag-writer.py              # Thin launcher wrapper
src/
  main.py                  # MainWindow (mixin composition) + main()
  tag_writer/
    constants.py           # Version, app metadata
    config.py              # Config class, SingleInstanceChecker
    platform.py            # Windows taskbar integration
    exiftool_utils.py      # ExifTool path resolution, persistent process
    image_utils.py         # PIL image loading, thumbnails, zoom
    file_utils.py          # File scanning, backup, metadata reading
    metadata.py            # MetadataManager (IPTC/XMP/EXIF)
    theme.py               # ThemeManager + 8 themes
    menu.py                # MenuMixin
    window.py              # WindowMixin
    navigation.py          # NavigationMixin
    file_ops.py            # FileOpsMixin
    theme_mixin.py         # ThemeMixin
    help.py                # HelpMixin
    updates.py             # UpdatesMixin
    dialogs/               # ThemeDialog, PreferencesDialog
    widgets/               # MetadataPanel, ImageViewer, FullImageViewer
tools/
  exiftool.exe             # Bundled ExifTool binary
```

## Requirements

- Python 3.8+
- PyQt6
- Pillow (PIL)
- pyexiftool
- ExifTool (bundled in `tools/` or available on system PATH)

## Usage

```bash
# Run the application
python tag-writer.py

# Open a specific image
python tag-writer.py path/to/image.jpg
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open file |
| Ctrl+S | Save metadata |
| Ctrl+E | Export metadata to JSON |
| Ctrl+I | Import metadata from JSON |
| Left/Right arrows | Previous/Next image |
| Ctrl+Plus/Minus | Zoom UI in/out |
| Ctrl+0 | Reset UI zoom |
| Ctrl+D | Toggle dark mode |

