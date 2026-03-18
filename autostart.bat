@echo off
REM HIOKI Resistance Meter - Windows Startup Batch Script
REM Uses global Python installation (no venv)
REM Place this in Windows Startup folder to auto-start after boot

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Navigate to application directory
cd /d "%SCRIPT_DIR%"

REM Run the application using global Python (no venv needed)
python main.py

endlocal
