@echo off
echo Starting TagWriter...
cd /d "C:\Users\juren\Projects\tag-writer"
python tag-writer.py
if errorlevel 1 (
    echo.
    echo Error: TagWriter failed to start.
    echo Make sure Python and required dependencies are installed.
    echo.
    pause
)