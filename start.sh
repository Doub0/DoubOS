#!/bin/bash
# DoubOS Quick Launcher for Linux/Mac
# Make executable: chmod +x start.sh
# Run: ./start.sh

echo "========================================"
echo "   DoubOS Quick Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from python.org"
    exit 1
fi

echo "Python detected!"
echo ""
echo "Choose launch mode:"
echo ""
echo "1. Launcher Menu (recommended)"
echo "2. Full System with Login"
echo "3. Quick Test (auto-login)"
echo "4. Run Tests"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting DoubOS Launcher..."
        python3 launcher.py
        ;;
    2)
        echo ""
        echo "Starting DoubOS with login screen..."
        python3 doubos_gui.py
        ;;
    3)
        echo ""
        echo "Starting DoubOS (auto-login)..."
        python3 doubos_test.py
        ;;
    4)
        echo ""
        echo "Running comprehensive tests..."
        python3 test_comprehensive.py
        echo ""
        read -p "Press Enter to continue..."
        ;;
    *)
        echo ""
        echo "Invalid choice. Starting launcher menu..."
        python3 launcher.py
        ;;
esac

echo ""
echo "DoubOS has exited."
