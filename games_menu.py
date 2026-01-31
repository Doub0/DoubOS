"""
Games Menu Application for DoubOS
"""

import tkinter as tk
import subprocess
import sys
import os


class GamesMenuApp(tk.Frame):
    """Games menu - launcher for available games"""
    
    def __init__(self, parent_frame, window_manager=None):
        super().__init__(parent_frame, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        self.window_manager = window_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup games menu"""
        # Title
        title = tk.Label(self, text="🎮 Games Library",
                        bg="#1e1e2e", fg="#cdd6f4",
                        font=("Segoe UI", 18, "bold"))
        title.pack(pady=20)
        
        # Games list
        games_frame = tk.Frame(self, bg="#1e1e2e")
        games_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        games = [
            {
                "name": "🌾 Croptopia",
                "desc": "Current Croptopia build (croptopia_python main.py)",
                "cmd": self.launch_croptopia
            }
        ]
        
        for game in games:
            self.create_game_card(games_frame, game)
            
    def create_game_card(self, parent, game):
        """Create a game card"""
        card = tk.Frame(parent, bg="#313244", relief=tk.RAISED, bd=2)
        card.pack(fill=tk.X, pady=10, padx=10)
        
        # Game name and description
        info_frame = tk.Frame(card, bg="#313244")
        info_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(info_frame, text=game["name"],
                bg="#313244", fg="#89b4fa",
                font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        
        tk.Label(info_frame, text=game["desc"],
                bg="#313244", fg="#cdd6f4",
                font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(5, 0))
        
        # Play button
        if game["cmd"]:
            btn = tk.Button(info_frame, text="▶ Play Game",
                           bg="#a6e3a1", fg="#1e1e2e",
                           font=("Segoe UI", 10, "bold"),
                           relief=tk.FLAT, cursor="hand2",
                           command=game["cmd"])
            btn.pack(anchor=tk.E, pady=(10, 0))
            
    def launch_croptopia(self):
        """Launch current Croptopia build (croptopia_python)"""
        try:
            repo_root = os.getcwd()
            venv_python = os.path.join(repo_root, ".venv", "Scripts", "python.exe")
            python_exe = venv_python if os.path.exists(venv_python) else sys.executable
            subprocess.Popen([python_exe, "main.py"], cwd=os.path.join(repo_root, "croptopia_python"))
        except Exception:
            import tkinter.messagebox as mb
            mb.showerror("Croptopia", "Failed to launch Croptopia")
