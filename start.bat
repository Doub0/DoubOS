@echo off
REM DoubOS Quick Launcher for Windows
REM Double-click this file to start DoubOS

echo ========================================
echo    DoubOS Quick Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo Python detected!
echo.
echo Choose launch mode:
echo.
echo 1. Launcher Menu (recommended)
echo 2. Full System with Login
echo 3. Quick Test (auto-login)
echo 4. Run Tests
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting DoubOS Launcher...
    python launcher.py
) else if "%choice%"=="2" (
    echo.
    echo Starting DoubOS with login screen...
    python doubos_gui.py
) else if "%choice%"=="3" (
    echo.
    echo Starting DoubOS (auto-login)...
    python doubos_test.py
) else if "%choice%"=="4" (
    echo.
    echo Running comprehensive tests...
    python test_comprehensive.py
    pause
) else (
    echo.
    echo Invalid choice. Starting launcher menu...
    python launcher.py
)

echo.
echo DoubOS has exited.
pause
