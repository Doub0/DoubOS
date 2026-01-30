@echo off
echo.
echo ========================================
echo    DoubOS Desktop - Windows Launcher
echo ========================================
echo.
echo Starting DoubOS GUI...
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.7 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3,7) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.7 or higher required!
    echo.
    echo Current version:
    python --version
    echo.
    pause
    exit /b 1
)

REM Launch DoubOS
echo Python found! Launching DoubOS...
echo.

python doubos_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: DoubOS failed to start!
    echo.
    pause
    exit /b 1
)

echo.
echo DoubOS closed successfully.
echo.
