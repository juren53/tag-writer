# -*- mode: python ; coding: utf-8 -*-

# Tag Writer - PyInstaller spec file for Windows executable
# Version: 0.1.6a
# Updated: 2026-01-05

a = Analysis(
    ['tag-writer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ICON_tw.ico', '.'),  # Include icon file in the bundle
        ('ICON_tw.png', '.'),  # Include PNG fallback
    ],
    hiddenimports=[],
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
