"""
DoubOS Window-Based Applications
Applications that run inside simulation windows
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import random


class SimulatedApp:
    """Base class for apps that run in simulation windows"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        
    def setup_ui(self):
        """Override this in subclasses"""
        pass
        
    def cleanup(self):
        """Cleanup when window closes"""
        pass


class TerminalApp(SimulatedApp):
    """Terminal application inside simulation"""
    
    def __init__(self, parent_frame, kernel=None, filesystem=None, user_manager=None):
        self.kernel = kernel
        self.filesystem = filesystem
        self.user_manager = user_manager
        self.current_dir = "/"
        self.command_history = []
        self.history_index = -1
        super().__init__(parent_frame)
        
    def setup_ui(self):
        """Setup terminal UI"""
        # Output area
        self.output = scrolledtext.ScrolledText(self.parent_frame, 
                                               bg="#0f0f1e", fg="#89b4fa",
                                               font=("Courier New", 10),
                                               height=20)
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output.config(state=tk.DISABLED)
        
        # Input area
        input_frame = tk.Frame(self.parent_frame, bg="#313244")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(input_frame, text="$ ", bg="#313244", 
                fg="#89b4fa", font=("Courier New", 10)).pack(side=tk.LEFT)
        
        self.input_field = tk.Entry(input_frame, bg="#0f0f1e", fg="#cdd6f4",
                                   font=("Courier New", 10),
                                   insertbackground="#cdd6f4")
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_field.bind("<Return>", lambda e: self.execute_command())
        self.input_field.bind("<Up>", self.history_up)
        self.input_field.bind("<Down>", self.history_down)
        self.input_field.focus()
        
        # Welcome message
        self.print_output("DoubOS Terminal v1.0\nType 'help' for commands\n", color="#a6e3a1")
        
    def execute_command(self):
        """Execute a command"""
        command = self.input_field.get()
        self.input_field.delete(0, tk.END)
        
        if not command:
            return
            
        self.print_output(f"$ {command}", color="#cdd6f4")
        self.command_history.append(command)
        self.history_index = -1
        
        result = self.run_command(command)
        if result:
            self.print_output(result)
        
    def run_command(self, command):
        """Run a command"""
        parts = command.split()
        if not parts:
            return ""
            
        cmd = parts[0].lower()
        
        if cmd == "help":
            return """Available commands:
ls, cd, pwd, mkdir, touch, cat, rm
whoami, uptime, date, clear
cowsay, fortune, hacker, matrix, joke"""
        elif cmd == "ls":
            return "📁 Documents  📁 Downloads  📁 Pictures  📁 Projects"
        elif cmd == "pwd":
            return self.current_dir
        elif cmd == "cd":
            if len(parts) > 1:
                self.current_dir = parts[1]
            return ""
        elif cmd == "whoami":
            return "admin"
        elif cmd == "uptime":
            return "System uptime: 2 hours 34 minutes"
        elif cmd == "date":
            from datetime import datetime
            return datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        elif cmd == "clear":
            self.output.config(state=tk.NORMAL)
            self.output.delete(1.0, tk.END)
            self.output.config(state=tk.DISABLED)
            return ""
        elif cmd == "cowsay":
            msg = " ".join(parts[1:]) if len(parts) > 1 else "Hello!"
            return f" {('_' * (len(msg) + 2))}\n< {msg} >\n {('-' * (len(msg) + 2))}\n        \\\\   ^__^\n         \\\\  (oo)\\\\_______"
        elif cmd == "fortune":
            quotes = [
                "The best way to predict the future is to invent it.",
                "Code is poetry written in a language that also talks to machines.",
                "In computing, the only constant is change."
            ]
            return random.choice(quotes)
        elif cmd == "hacker":
            return "🔓 ACCESSING MAINFRAME...\n████████░░ 82%\n✓ ACCESS GRANTED"
        elif cmd == "matrix":
            return "".join([chr(random.randint(33, 126)) for _ in range(150)])
        elif cmd == "joke":
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "How many programmers does it take to change a light bulb? None, that's hardware!"
            ]
            return random.choice(jokes)
        else:
            return f"Command not found: {cmd}"
            
    def print_output(self, text, color="#cdd6f4"):
        """Print text to output"""
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
        
    def history_up(self, event):
        """Navigate history up"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, self.command_history[-(self.history_index + 1)])
        return "break"
            
    def history_down(self, event):
        """Navigate history down"""
        if self.history_index > 0:
            self.history_index -= 1
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, self.command_history[-(self.history_index + 1)])
        elif self.history_index == 0:
            self.history_index = -1
            self.input_field.delete(0, tk.END)
        return "break"


class FileExplorerApp(SimulatedApp):
    """File Explorer"""
    
    def __init__(self, parent_frame, filesystem=None):
        super().__init__(parent_frame)
        
    def setup_ui(self):
        """Setup file explorer"""
        addr_frame = tk.Frame(self.parent_frame, bg="#313244")
        addr_frame.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Label(addr_frame, text="📍 /home/admin", bg="#313244", 
                fg="#cdd6f4", font=("Segoe UI", 10)).pack(anchor=tk.W, padx=5)
        
        tree = ttk.Treeview(self.parent_frame, height=20)
        tree.heading("#0", text="Files")
        tree.column("#0", width=300)
        
        tree.insert("", "end", text="📁 Documents")
        tree.insert("", "end", text="📁 Downloads")
        tree.insert("", "end", text="📄 README.md")
        tree.insert("", "end", text="📄 notes.txt")
        
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


class TextEditorApp(SimulatedApp):
    """Text Editor"""
    
    def setup_ui(self):
        """Setup editor"""
        toolbar = tk.Frame(self.parent_frame, bg="#313244")
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        for btn_text in ["📄 New", "📂 Open", "💾 Save"]:
            tk.Button(toolbar, text=btn_text, bg="#89b4fa", fg="#1e1e2e").pack(side=tk.LEFT, padx=2)
        
        self.text = scrolledtext.ScrolledText(self.parent_frame,
                                             bg="#0f0f1e", fg="#cdd6f4",
                                             font=("Courier New", 10))
        self.text.pack(fill=tk.BOTH, expand=True, padx=5)


class CalculatorApp(SimulatedApp):
    """Calculator"""
    
    def setup_ui(self):
        """Setup calculator"""
        self.display = tk.Entry(self.parent_frame, font=("Segoe UI", 20, "bold"),
                               bg="#0f0f1e", fg="#89b4fa", justify=tk.RIGHT)
        self.display.pack(fill=tk.X, pady=10, padx=10)
        
        buttons = [
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]
        
        for row in buttons:
            row_frame = tk.Frame(self.parent_frame, bg="#1e1e2e")
            row_frame.pack(fill=tk.X, padx=10, pady=5)
            
            for btn_text in row:
                tk.Button(row_frame, text=btn_text, font=("Segoe UI", 12, "bold"),
                         bg="#89b4fa", fg="#1e1e2e", width=6).pack(side=tk.LEFT, padx=5, expand=True)


class SettingsApp(SimulatedApp):
    """Settings"""
    
    def setup_ui(self):
        """Setup settings"""
        tk.Label(self.parent_frame, text="⚙️ System Settings",
                bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, padx=10, pady=10)
        
        tk.Label(self.parent_frame, text="Themes:",
                bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10)).pack(anchor=tk.W, padx=10)
        
        for theme in ["✓ Catppuccin Mocha", "Dracula", "Nord", "Tokyo Night"]:
            tk.Label(self.parent_frame, text=theme,
                    bg="#1e1e2e", fg="#a6e3a1", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=20, pady=2)
