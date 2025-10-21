@echo off
REM Startup script for AiChemist Transmutation Codex

echo Starting AiChemist Transmutation Codex...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.13+ and try again
    pause
    exit /b 1
)

REM Run the startup script
python scripts/start_app.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
