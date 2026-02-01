@echo off
REM Croptopia Game Launcher
REM Fixed: February 1, 2026

echo ========================================
echo    CROPTOPIA GAME LAUNCHER
echo ========================================
echo.
echo Starting Croptopia...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo Game exited with errors
    echo.
    echo Try running: python croptopia_complete_1to1.py
    echo ========================================
    pause
)
