# -*- mode: python ; coding: utf-8 -*-

# Tag Writer - PyInstaller spec file for Windows executable
# Version: 0.2.1
# Updated: 2026-02-17

import os

a = Analysis(
    ['tag-writer.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('ICON_tw.ico', '.'),  # Include icon file in the bundle
        ('ICON_tw.png', '.'),  # Include PNG fallback
        ('tools/exiftool.exe', 'tools'),  # Bundle ExifTool
        ('Docs', 'Docs'),  # Include documentation
        ('CHANGELOG.md', '.'),  # Include changelog
        ('github_version_checker.py', '.'),  # Version checker module
    ],
    hiddenimports=['tag_writer', 'pyqt_app_info', 'pyqt_app_info.qt'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tag-writer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ICON_tw.ico',  # Use ICO file for Windows taskbar icon
)
