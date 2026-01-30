#!/bin/bash

echo ""
echo "========================================"
echo "   DoubOS Desktop - Linux/Mac Launcher"
echo "========================================"
echo ""
echo "Starting DoubOS GUI..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.7 or higher:"
    echo ""
    echo "Ubuntu/Debian: sudo apt install python3 python3-tk"
    echo "Fedora: sudo dnf install python3 python3-tkinter"
    echo "Arch: sudo pacman -S python python-tk"
    echo "macOS: brew install python-tk"
    echo ""
    exit 1
fi

# Check Python version
python3 -c "import sys; exit(0 if sys.version_info >= (3,7) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.7 or higher required!"
    echo ""
    echo "Current version:"
    python3 --version
    echo ""
    exit 1
fi

# Check for tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Tkinter is not installed!"
    echo ""
    echo "Please install tkinter:"
    echo ""
    echo "Ubuntu/Debian: sudo apt install python3-tk"
    echo "Fedora: sudo dnf install python3-tkinter"
    echo "Arch: sudo pacman -S tk"
    echo "macOS: brew install python-tk"
    echo ""
    exit 1
fi

# Launch DoubOS
echo "Python found! Launching DoubOS..."
echo ""

python3 doubos_gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: DoubOS failed to start!"
    echo ""
    exit 1
fi

echo ""
echo "DoubOS closed successfully."
echo ""
