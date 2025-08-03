# TagWriter AppImage Build Workflows

This directory contains Warp workflows for automating the AppImage build process for TagWriter.

## Available Workflows

### 1. `build-appimage.yaml` - Full Build Workflow
**Complete, production-ready AppImage build with testing and validation**

**Features:**
- ✅ Comprehensive build process with error checking
- ✅ Automatic dependency verification
- ✅ AppImage testing and validation  
- ✅ Detailed build logging with emojis
- ✅ Cleanup of temporary files
- ✅ Build summary with usage instructions

**Usage:**
```bash
warp-cli run .warp/workflows/build-appimage.yaml
```

### 2. `quick-build.yaml` - Fast Build Workflow  
**Streamlined build for rapid development iterations**

**Features:**
- ⚡ Fast execution (3 steps vs 11 steps)
- ⚡ Minimal logging and validation
- ⚡ No dependency checking or testing
- ⚡ Perfect for development builds

**Usage:**
```bash
warp-cli run .warp/workflows/quick-build.yaml
```

### 3. `test-appimage.yaml` - AppImage Testing Workflow
**Comprehensive testing and validation of existing AppImages**

**Features:**
- 🧪 Complete functionality testing
- 🔍 Dependency verification
- 🚀 Launch and performance testing
- 🔗 Desktop integration validation
- 📊 Detailed test reporting

**Usage:**
```bash
warp-cli run .warp/workflows/test-appimage.yaml
```

## Prerequisites

Before running these workflows, ensure you have:

1. **Python 3** with PyQt6 installed
2. **ExifTool** available in your system
3. **appimagetool** - either:
   - Local copy: `./appimagetool` (recommended)
   - System installation: `sudo apt install appimagetool` or similar

### Installing appimagetool (if not available)

```bash
# Download the latest appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
mv appimagetool-x86_64.AppImage appimagetool
```

## Workflow Configuration

Both workflows use these environment variables (automatically set):

| Variable | Value | Description |
|----------|-------|-------------|
| `APP_NAME` | `TagWriter` | Application name for the AppImage |
| `APP_VERSION` | `0.07z` | Current version from tag-writer.py |
| `ARCH` | `x86_64` | Target architecture |
| `APPDIR_NAME` | `TagWriter.AppDir` | Temporary build directory |

## Output

Both workflows generate:
- **AppImage file**: `TagWriter-0.07z-x86_64.AppImage`
- **Desktop integration**: Proper MIME types for image files
- **Icon integration**: Uses ICON_tw.ico/png for the application icon

## File Structure

The workflows expect this project structure:
```
tag-writer/
├── tag-writer.py          # Main application script
├── ICON_tw.ico           # Windows icon file  
├── ICON_tw.png           # Linux icon file
├── Docs/                 # Documentation (optional)
├── appimagetool          # AppImage build tool
└── .warp/
    └── workflows/
        ├── build-appimage.yaml
        ├── quick-build.yaml
        └── README.md
```

## Troubleshooting

### Common Issues

**1. "appimagetool not found"**
```bash
# Download and install appimagetool locally
wget -O appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool
```

**2. "Permission denied" errors**
```bash
# Ensure scripts are executable
chmod +x tag-writer.py
chmod +x appimagetool
```

**3. "PyQt6 not found"**
```bash
# Install PyQt6
pip install PyQt6
```

**4. "ExifTool not found"**
```bash
# Install ExifTool
sudo apt install exiftool  # Ubuntu/Debian
sudo dnf install exiftool  # Fedora
brew install exiftool      # macOS
```

### Build Validation

The full workflow (`build-appimage.yaml`) includes these validation steps:
- ✅ Dependency checking (Python, PyQt6, ExifTool)
- ✅ AppImage functionality testing
- ✅ File size and architecture verification
- ✅ Build artifact cleanup

### Manual Testing

After building, test your AppImage:
```bash
# Test direct execution
./TagWriter-0.07z-x86_64.AppImage

# Test with file argument
./TagWriter-0.07z-x86_64.AppImage /path/to/image.jpg

# Test help/version
./TagWriter-0.07z-x86_64.AppImage --help
```

## Development Tips

- Use **quick-build** for frequent development builds
- Use **build-appimage** for release builds
- The workflows automatically handle file permissions and paths
- Documentation from `Docs/` is automatically included if present
- Both ICO and PNG icons are supported

## Workflow Customization

To modify the workflows for your needs:

1. **Change version**: Update `APP_VERSION` in the `env` section
2. **Add build steps**: Insert new steps in the `steps` array
3. **Modify file copying**: Edit the "Copy application files" step
4. **Change architecture**: Modify the `ARCH` environment variable

## Integration with CI/CD

These workflows can be integrated with CI/CD systems:

```yaml
# Example GitHub Actions integration
- name: Build AppImage
  run: |
    # Install warp-cli if needed
    warp-cli run .warp/workflows/build-appimage.yaml
    
- name: Upload AppImage
  uses: actions/upload-artifact@v3
  with:
    name: TagWriter-AppImage
    path: TagWriter-*.AppImage
```

## Support

For issues with:
- **Workflows**: Check this README and workflow comments
- **AppImage creation**: See [AppImage documentation](https://docs.appimage.org/)
- **TagWriter app**: Check the main project README
