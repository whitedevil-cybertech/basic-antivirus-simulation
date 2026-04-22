@echo off
REM Antivirus Scanner GUI Launcher for Windows

title Antivirus Scanner GUI
color 0A

echo.
echo ========================================================================
echo  Antivirus Scanner - Professional Threat Detection
echo  GUI Launcher (Phase 3 Complete)
echo ========================================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ or add it to your PATH
    pause
    exit /b 1
)

REM Check if PyQt6 is installed
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyQt6 is not installed
    echo Installing PyQt6...
    python -m pip install PyQt6
)

echo.
echo Starting GUI...
echo.

REM Launch the GUI
python launch_gui.py

pause
