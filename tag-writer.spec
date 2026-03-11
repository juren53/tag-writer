# -*- mode: python ; coding: utf-8 -*-

# Tag Writer - PyInstaller spec file for Windows executable
# Version: 0.2.3
# Updated: 2026-03-11
#
# Product name and version are pulled dynamically from src/tag_writer/constants.py
# via the shared helper at C:\Users\juren\Projects\_build_tools\version_info_helper.py

import os
import sys

# --- Dynamic version info ---------------------------------------------------
# Pull APP_NAME, APP_VERSION, APP_ORGANIZATION from constants.py
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from tag_writer.constants import APP_NAME, APP_VERSION, APP_ORGANIZATION

# Use shared helper to generate the Windows version resource file
sys.path.insert(0, r'C:\Users\juren\Projects\_build_tools')
from version_info_helper import make_version_info

version_file = make_version_info(
    app_name=APP_NAME,
    version_str=APP_VERSION,
    company=APP_ORGANIZATION,
    exe_name='tag-writer',
    copyright_years='2024-2026',
    output_path='_version_info.txt',
)
# ----------------------------------------------------------------------------

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
    version=version_file,  # Windows Properties/Details panel metadata
)
