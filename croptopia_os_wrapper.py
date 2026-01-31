"""
Croptopia Game Wrapper for DoubOS Integration

This module launches the current Croptopia Python build from the DoubOS window manager.
Runs croptopia_python/main.py as a separate process and shows status inside the DoubOS window.
"""

import tkinter as tk
import os
import sys
import subprocess


class RootProxy:
    """
    Proxy object that mimics tk.Tk interface for tk.Frame.
    
    CroptopiaGame expects a tk.Tk root window with methods like:
    - title()
    - geometry()
    - resizable()
    - pack()
    - after()
    - bind()
    
    This proxy redirects these calls to work with a Frame instead.
    """
    
    def __init__(self, frame):
        """Initialize proxy with a frame."""
        self.frame = frame
        self._width = 800
        self._height = 600
        
    def title(self, text):
        """Title method (no-op for frame, handled by window manager)."""
        pass
    
    def geometry(self, geometry_string):
        """Parse geometry and update frame size."""
        # Format: "WIDTHxHEIGHT+X+Y" or "WIDTHxHEIGHT"
        try:
            if 'x' in geometry_string.lower():
                parts = geometry_string.lower().split('+')
                dims = parts[0].split('x')
                self._width = int(dims[0])
                self._height = int(dims[1])
        except:
            pass
    
    def resizable(self, width, height):
        """Resizable method (no-op for windowed game)."""
        pass
    
    def after(self, ms, func=None, *args):
        """Schedule a callback after delay."""
        return self.frame.after(ms, func, *args)
    
    def bind(self, sequence, func, add=None):
        """Bind event to frame."""
        return self.frame.bind(sequence, func, add)
    
    def __getattr__(self, name):
        """Fallback to frame for other attributes."""
        return getattr(self.frame, name)


class CroptopiaGameWindow(tk.Frame):
    """
    Wrapper that makes CroptopiaGame compatible with DoubOS window manager.
    
    The game runs inside a Tkinter Frame that can be embedded in the DoubOS
    desktop environment. This allows the game to be launched as a windowed
    application from the Games menu.
    """
    
    def __init__(self, parent_frame):
        """
        Initialize the Croptopia game wrapper.
        
        Args:
            parent_frame: The parent Tkinter frame (provided by window manager)
        """
        super().__init__(parent_frame, bg="#1e1e2e")
        self.parent_frame = parent_frame
        self.process = None
        self.running = False

        # Launch current Croptopia build
        self._create_game()
        
    def _create_game(self):
        """Launch the current Croptopia build as a subprocess."""
        try:
            print("🎮 Launching Croptopia (croptopia_python)...")

            repo_root = os.path.dirname(os.path.abspath(__file__))
            game_dir = os.path.join(repo_root, "croptopia_python")
            game_entry = os.path.join(game_dir, "main.py")

            venv_python = os.path.join(repo_root, ".venv", "Scripts", "python.exe")
            python_exe = venv_python if os.path.exists(venv_python) else sys.executable

            if not os.path.exists(game_entry):
                raise FileNotFoundError(f"Croptopia entry not found: {game_entry}")

            status = tk.Label(
                self,
                text="Launching Croptopia...",
                bg="#1e1e2e",
                fg="#cdd6f4",
                font=("Segoe UI", 12)
            )
            status.pack(expand=True)

            self.process = subprocess.Popen(
                [python_exe, "main.py"],
                cwd=game_dir
            )

            self.running = True
            status.config(text="Croptopia is running in a separate window.")
            print("✓ Croptopia process started")
        except Exception as e:
            print(f"✗ Error launching Croptopia: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
            error_label = tk.Label(
                self,
                text=f"Error launching Croptopia:\n{str(e)}",
                bg="#1e1e2e",
                fg="#f38ba8",
                font=("Segoe UI", 12)
            )
            error_label.pack(expand=True)
            
    def cleanup(self):
        """Cleanup when window is closed."""
        self.running = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
            except Exception:
                pass


class UltimatecroptopiaGame(tk.Frame):
    """
    Alias for CroptopiaGameWindow for backwards compatibility.
    This name is used by games_menu.py during import.
    """
    
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.wrapper = CroptopiaGameWindow(parent_frame)
        self.wrapper.pack(fill=tk.BOTH, expand=True)
