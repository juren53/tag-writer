# TagWriter Setup Guide

## Installation Complete ✅

TagWriter has been successfully installed and is ready to use!

### What Was Installed

- **TagWriter Application**: Cloned from `github.com/juren53/tag-writer`
- **Python Dependencies**: 
  - PyExifTool==0.5.6
  - PyQt6==6.10.1 (upgraded from 6.4.2 for better compatibility)
  - PyQt6-sip==13.10.3
  - PyQt6-WebEngine==6.10.0
- **External Dependency**: ExifTool v13.43 (already installed)

### Location
```
C:\Users\juren\Projects\tag-writer\
```

### How to Run

#### Method 1: Direct Python Execution
```bash
cd "C:\Users\juren\Projects\tag-writer"
python tag-writer.py
```

#### Method 2: Using the Run Script
```bash
cd "C:\Users\juren\Projects\tag-writer"
run-tag-writer.bat
```

### Features Verified ✅

1. **GUI Launch**: Application starts successfully
2. **ExifTool Integration**: v13.43 detected and working
3. **Image Loading**: Successfully loads JPG, TIFF, PNG files
4. **Metadata Reading**: EXIF and IPTC metadata extraction working
5. **Theme System**: Dark theme applied successfully
6. **UI Scaling**: 100% zoom level set

### Supported File Types

- JPEG / JPG
- TIFF / TIF  
- PNG

### Key IPTC Metadata Fields

- Headline (Title)
- Caption-Abstract (Description)
- Object Name (Accession Number)
- By-line (Photographer)
- By-line Title (Institutional Creator)
- Credit
- Source (Collection)
- Copyright Notice (Restrictions)
- Writer-Editor (Archivist/Editor)

### Troubleshooting

If you encounter any issues:

1. **ExifTool Not Found**: Ensure ExifTool is in your system PATH
2. **DLL Loading Issues**: The PyQt6 upgrade should have resolved this
3. **Image Loading Issues**: Verify the image file is not corrupted

### Next Steps

1. Launch the application using one of the methods above
2. Test with your own image files
3. Explore the metadata editing capabilities
4. Check the built-in Help menu (User Guide, Glossary, Keyboard Shortcuts)

### Documentation

Additional documentation is available in the `Docs/` folder:
- User Guide: `Docs/user-guide.md`
- Glossary: `Docs/glossary.md`
- Keyboard Shortcuts: `Docs/KeyBoard-ShortCuts.md`

---

**Status**: ✅ Ready to Use
**Date**: 2025-12-15
**Version**: Latest from main branch