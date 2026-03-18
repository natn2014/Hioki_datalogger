@echo off
REM HIOKI Resistance Meter - Windows Startup Batch Script
REM This script starts the HIOKI Resistance Meter application
REM Place this in Windows Startup folder to auto-start after boot

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Navigate to application directory
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and run the application
call venv\Scripts\activate.bat

REM Install/update dependencies silently
pip install -q -r requirements.txt

REM Run the application (minimized window)
python main.py

REM On exit, deactivate venv (this won't execute until app closes)
deactivate

endlocal
