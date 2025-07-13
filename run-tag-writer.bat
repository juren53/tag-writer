@echo off
REM Simple batch file to run tag-writer with proper icon association
REM This helps Windows recognize the application as a distinct entity

REM Set the application identity
set PYTHONPATH=%~dp0
cd /d "%~dp0"

REM Run the application
python tag-writer.py

REM Pause if there's an error (optional)
if errorlevel 1 pause
