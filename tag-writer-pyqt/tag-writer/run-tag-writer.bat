@echo off
REM ========================================================
REM Tag Writer Application Launcher
REM ========================================================
REM This batch file checks if the tag-writer.exe executable
REM exists in the dist directory and launches it if found.
REM If the executable is not found, an error message is displayed.
REM ========================================================

echo Checking for Tag Writer executable...

if exist dist\tag-writer.exe (
    echo Found Tag Writer executable. Launching application...
    start "" "dist\tag-writer.exe"
) else (
    echo ERROR: Tag Writer executable not found in the dist directory.
    echo Please ensure the application has been built using PyInstaller.
    echo.
    echo You can build the application by running:
    echo     pyinstaller --onefile --windowed --icon="resources/icons/icon.png" --name="tag-writer" --add-data="resources;resources" run-tag-writer.py
    echo.
    pause
)

