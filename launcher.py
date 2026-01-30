#!/usr/bin/env python3
"""
DoubOS GUI - Main Launcher with options
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import subprocess
import os


class LauncherMenu:
    """Main launcher menu"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DoubOS - Launcher")
        self.root.geometry("500x400")
        self.root.configure(bg="#1e1e2e")
        
        # Colors
        self.colors = {
            "bg": "#1e1e2e",
            "panel": "#313244",
            "accent": "#89b4fa",
            "text": "#cdd6f4",
            "success": "#a6e3a1",
            "danger": "#f38ba8",
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup launcher UI"""
        # Title
        title = tk.Label(self.root, text="🖥️  DoubOS Launcher", 
                        font=("Segoe UI", 24, "bold"),
                        bg=self.colors["bg"], fg=self.colors["accent"])
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(self.root, text="Advanced Desktop Operating System",
                           font=("Segoe UI", 10),
                           bg=self.colors["bg"], fg=self.colors["text"])
        subtitle.pack(pady=(0, 30))
        
        # Buttons
        button_frame = tk.Frame(self.root, bg=self.colors["bg"])
        button_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        options = [
            ("🔐 Login with credentials", self.launch_full),
            ("⚡ Quick test (auto-login)", self.launch_test),
            ("🧪 Run comprehensive test", self.launch_comprehensive),
            ("❌ Exit", self.exit_launcher),
        ]
        
        for text, cmd in options:
            btn = tk.Button(button_frame, text=text,
                           font=("Segoe UI", 12),
                           bg=self.colors["accent"], fg="#1e1e2e",
                           relief=tk.FLAT, cursor="hand2",
                           command=cmd)
            btn.pack(fill=tk.X, pady=8)
            
        # Info
        info = tk.Label(self.root, 
                       text="Choose how to start DoubOS",
                       font=("Segoe UI", 9),
                       bg=self.colors["bg"], fg=self.colors["text"])
        info.pack(side=tk.BOTTOM, pady=10)
        
    def launch_full(self):
        """Launch full system with login"""
        self.root.destroy()
        subprocess.Popen([sys.executable, "doubos_gui.py"], 
                        cwd=os.path.dirname(os.path.abspath(__file__)))
        
    def launch_test(self):
        """Launch with auto-login"""
        self.root.destroy()
        subprocess.Popen([sys.executable, "doubos_test.py"],
                        cwd=os.path.dirname(os.path.abspath(__file__)))
        
    def launch_comprehensive(self):
        """Run comprehensive test"""
        self.root.destroy()
        subprocess.Popen([sys.executable, "test_comprehensive.py"],
                        cwd=os.path.dirname(os.path.abspath(__file__)))
        
    def exit_launcher(self):
        """Exit launcher"""
        self.root.destroy()
        
    def run(self):
        """Run launcher"""
        self.root.mainloop()


if __name__ == "__main__":
    launcher = LauncherMenu()
    launcher.run()
