#!/usr/bin/env python3
"""
CROPTOPIA LAUNCHER - Main Entry Point
======================================

This file redirects to the actual game implementation.
The real game code is in croptopia_python/main.py

Run this from the DoubOS directory to launch Croptopia.
"""

import os
import sys
import subprocess

def main():
    """Launch the Croptopia game from the correct directory"""
    
    print("=" * 60)
    print("CROPTOPIA GAME LAUNCHER")
    print("=" * 60)
    print()
    print("Launching Croptopia from croptopia_python/main.py...")
    print()
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    game_dir = os.path.join(script_dir, "croptopia_python")
    game_main = os.path.join(game_dir, "main.py")
    
    # Check if the game exists
    if not os.path.exists(game_main):
        print(f"ERROR: Game not found at {game_main}")
        print()
        print("Available options:")
        print("  1. Run from croptopia_python folder:")
        print("     cd croptopia_python && python main.py")
        print()
        print("  2. Run the complete Tkinter version:")
        print("     python croptopia_complete_1to1.py")
        print()
        print("  3. Use the DoubOS launcher:")
        print("     python launcher.py")
        print()
        return 1
    
    # Launch the game
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=game_dir
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
        return 0
    except Exception as e:
        print(f"\nERROR: Failed to launch game: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
