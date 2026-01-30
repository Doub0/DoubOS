#!/usr/bin/env python3
"""
Quick test to verify the window system works
"""

import tkinter as tk
from window_manager import WindowManager, SimulationWindow
from windowed_apps import TerminalApp, FileExplorerApp, TextEditorApp, CalculatorApp, SettingsApp
from croptopia_sim import CroptopiaSim

def test_windows():
    """Test window manager"""
    print("Testing Window Manager...")
    
    # Create a root window
    root = tk.Tk()
    root.title("DoubOS Window Manager Test")
    root.geometry("1000x600")
    root.configure(bg="#1e1e2e")
    
    # Create desktop frame
    desktop_frame = tk.Frame(root, bg="#1e1e2e")
    desktop_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create window manager
    wm = WindowManager(desktop_frame)
    print("✓ Window manager created")
    
    # Test buttons to open windows
    button_frame = tk.Frame(root, bg="#313244")
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def open_term():
        wm.open_window("Terminal", 600, 300, TerminalApp, None, None, None)
    
    def open_files():
        wm.open_window("Files", 500, 300, FileExplorerApp, None)
    
    def open_editor():
        wm.open_window("Editor", 600, 400, TextEditorApp)
    
    def open_calc():
        wm.open_window("Calculator", 350, 400, CalculatorApp)
    
    def open_settings():
        wm.open_window("Settings", 500, 350, SettingsApp)
    
    def open_game():
        wm.open_window("Croptopia", 700, 550, CroptopiaSim)
    
    tk.Button(button_frame, text="Terminal", command=open_term, bg="#89b4fa", fg="#1e1e2e").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Files", command=open_files, bg="#89b4fa", fg="#1e1e2e").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Editor", command=open_editor, bg="#89b4fa", fg="#1e1e2e").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Calculator", command=open_calc, bg="#89b4fa", fg="#1e1e2e").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Settings", command=open_settings, bg="#89b4fa", fg="#1e1e2e").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Croptopia", command=open_game, bg="#a6e3a1", fg="#1e1e2e").pack(side=tk.LEFT, padx=5)
    
    print("✓ Test buttons created")
    print("\nWindow Manager Test Ready!")
    print("Click buttons to test window creation...")
    
    root.mainloop()

if __name__ == "__main__":
    test_windows()
