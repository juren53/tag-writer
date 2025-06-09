# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['tag-writer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('tag_writer', 'tag_writer'),  # Include the tag_writer module
        ('ICON_tw.ico', '.'),  # Include the icon
        ('ICON_tw.png', '.'),  # Include the PNG icon as well
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'tag_writer.models.metadata',
        'tag_writer.utils.file_operations',
        'tag_writer.utils.config',
        'tag_writer.utils.image_processing',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ExifTags',
    ],
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
    console=False,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ICON_tw.ico',  # Specify the icon file

    version_file=None,
)
