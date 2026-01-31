#!/usr/bin/env python3
"""
Croptopia - Integrated DoubOS Application Launcher
Launches Croptopia game engine in a window
"""

import tkinter as tk
from croptopia_engine_native import CroptopiaEngine
import threading
import pygame

def launch_croptopia_in_tkinter():
    """Launch Croptopia in a Tkinter window by embedding pygame."""
    import os
    os.environ['SDL_VIDEODRIVER'] = 'windowed'
    
    # Create dedicated window
    root = tk.Tk()
    root.title("Croptopia - Native Game Engine")
    root.geometry("1920x1080")
    root.resizable(False, False)
    
    # Launch game in thread
    def run_game():
        engine = CroptopiaEngine()
        engine.run()
    
    game_thread = threading.Thread(target=run_game, daemon=True)
    game_thread.start()
    
    try:
        root.mainloop()
    except:
        pass

def standalone_launch():
    """Launch Croptopia as standalone application."""
    engine = CroptopiaEngine()
    engine.run()

if __name__ == "__main__":
    # Launch standalone
    standalone_launch()
