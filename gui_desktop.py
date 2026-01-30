"""
DoubOS GUI - Desktop Environment
Full graphical user interface with window management
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import subprocess
import os
from window_manager import WindowManager
from windowed_apps import TerminalApp, FileExplorerApp, TextEditorApp, CalculatorApp, SettingsApp
from croptopia_ultimate import EnhancedCroptopia
from games_menu import GamesMenuApp


class DoubOSDesktop:
    """Main desktop environment"""
    
    def __init__(self, kernel, filesystem, user_manager):
        self.kernel = kernel
        self.filesystem = filesystem
        self.user_manager = user_manager
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("DoubOS Desktop")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e2e")
        
        # Theme colors
        self.colors = {
            "bg": "#1e1e2e",
            "panel": "#313244",
            "accent": "#89b4fa",
            "text": "#cdd6f4",
            "hover": "#45475a",
            "success": "#a6e3a1",
            "danger": "#f38ba8",
            "warning": "#f9e2af"
        }
        
        # Window management
        self.window_manager = None
        self.windows = []
        self.next_window_offset = 0
        
        # Desktop setup
        self.setup_desktop()
        self.setup_taskbar()
        
        # Create window manager AFTER desktop_frame exists
        self.window_manager = WindowManager(self.desktop_frame)
        print("✓ Window manager initialized")
        
        # Start system services
        self.update_clock()
        
    def setup_desktop(self):
        """Setup desktop area"""
        self.desktop_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.desktop_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup wallpaper first
        self.setup_wallpaper()
        
        # Desktop icons
        self.create_desktop_icons()
        
    def create_desktop_icons(self):
        """Create desktop shortcut icons"""
        icons = [
            ("💻 Terminal", self.open_terminal, 20, 20),
            ("📁 Files", self.open_file_explorer, 20, 120),
            ("⚙️ Settings", self.open_settings, 20, 220),
            ("📝 Text Editor", self.open_text_editor, 20, 320),
            ("🧮 Calculator", self.open_calculator, 20, 420),
            ("🎮 Games", self.open_games, 20, 520),
        ]
        
        for text, command, x, y in icons:
            self.create_icon(text, command, x, y)
            
    def create_icon(self, text, command, x, y):
        """Create a desktop icon"""
        icon_frame = tk.Frame(self.desktop_frame, bg=self.colors["bg"], 
                             cursor="hand2", width=80, height=100)
        icon_frame.place(x=x, y=y)
        icon_frame.pack_propagate(False)
        
        # Icon label
        lines = text.split(" ", 1)
        emoji = lines[0]
        name = lines[1] if len(lines) > 1 else ""
        
        emoji_label = tk.Label(icon_frame, text=emoji, font=("Segoe UI Emoji", 32),
                              bg=self.colors["bg"], fg=self.colors["text"])
        emoji_label.pack(pady=(5, 0))
        
        name_label = tk.Label(icon_frame, text=name, font=("Segoe UI", 9),
                             bg=self.colors["bg"], fg=self.colors["text"])
        name_label.pack()
        
        # Click handlers
        for widget in [icon_frame, emoji_label, name_label]:
            widget.bind("<Button-1>", lambda e: command())
            widget.bind("<Enter>", lambda e: self.icon_hover(icon_frame, True))
            widget.bind("<Leave>", lambda e: self.icon_hover(icon_frame, False))
            
    def icon_hover(self, frame, entering):
        """Handle icon hover effect"""
        if entering:
            frame.configure(bg=self.colors["hover"])
            for child in frame.winfo_children():
                child.configure(bg=self.colors["hover"])
        else:
            frame.configure(bg=self.colors["bg"])
            for child in frame.winfo_children():
                child.configure(bg=self.colors["bg"])
                
    def setup_wallpaper(self):
        """Setup desktop wallpaper"""
        canvas = tk.Canvas(self.desktop_frame, bg=self.colors["bg"], 
                          highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Gradient effect (simulated with rectangles)
        canvas.create_rectangle(0, 0, 1200, 200, 
                               fill="#1e1e2e", outline="")
        canvas.create_rectangle(0, 200, 1200, 400, 
                               fill="#262637", outline="")
        canvas.create_rectangle(0, 400, 1200, 600, 
                               fill="#2e2e40", outline="")
        
        # DoubOS logo
        canvas.create_text(600, 300, text="DoubOS", 
                          font=("Segoe UI", 72, "bold"),
                          fill="#89b4fa", anchor="center")
        canvas.create_text(600, 360, text="Desktop Environment", 
                          font=("Segoe UI", 18),
                          fill="#cdd6f4", anchor="center")
                          
    def setup_taskbar(self):
        """Setup taskbar at bottom"""
        self.taskbar = tk.Frame(self.root, bg=self.colors["panel"], 
                               height=50)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.taskbar.pack_propagate(False)
        
        # Start button
        self.start_btn = tk.Button(self.taskbar, text="⊞ START", 
                                   font=("Segoe UI", 11, "bold"),
                                   bg=self.colors["accent"], 
                                   fg="#1e1e2e",
                                   relief=tk.FLAT, 
                                   cursor="hand2",
                                   padx=20, pady=10,
                                   command=self.toggle_start_menu)
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Quick launch apps
        apps = [
            ("🌐", "Browser", self.open_browser),
            ("📧", "Mail", self.open_mail),
            ("🎵", "Music", self.open_music),
            ("🖼️", "Photos", self.open_photos),
        ]
        
        for emoji, tooltip, cmd in apps:
            btn = tk.Button(self.taskbar, text=emoji, 
                          font=("Segoe UI Emoji", 16),
                          bg=self.colors["panel"], 
                          fg=self.colors["text"],
                          relief=tk.FLAT, 
                          cursor="hand2",
                          command=cmd,
                          width=3)
            btn.pack(side=tk.LEFT, padx=2, pady=5)
            self.create_tooltip(btn, tooltip)
            
        # System tray (right side)
        self.tray = tk.Frame(self.taskbar, bg=self.colors["panel"])
        self.tray.pack(side=tk.RIGHT, padx=10)
        
        # Clock
        self.clock_label = tk.Label(self.tray, font=("Segoe UI", 10),
                                    bg=self.colors["panel"], 
                                    fg=self.colors["text"])
        self.clock_label.pack(side=tk.RIGHT, padx=10)
        
        # User info
        user = self.user_manager.get_current_user()
        user_text = f"👤 {user.username if user else 'Guest'}"
        user_label = tk.Label(self.tray, text=user_text, 
                             font=("Segoe UI", 9),
                             bg=self.colors["panel"], 
                             fg=self.colors["text"])
        user_label.pack(side=tk.RIGHT, padx=10)
        
        # System icons
        icons = [
            ("🔊", "Volume", self.show_volume),
            ("📶", "Network", self.show_network),
            ("🔋", "Battery", self.show_battery),
        ]
        
        for emoji, tooltip, cmd in icons:
            btn = tk.Button(self.tray, text=emoji, 
                          font=("Segoe UI Emoji", 12),
                          bg=self.colors["panel"], 
                          fg=self.colors["text"],
                          relief=tk.FLAT, 
                          cursor="hand2",
                          command=cmd)
            btn.pack(side=tk.RIGHT, padx=3)
            self.create_tooltip(btn, tooltip)
            
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, 
                           bg="#f9e2af", fg="#1e1e2e",
                           relief=tk.SOLID, borderwidth=1,
                           font=("Segoe UI", 8), padx=5, pady=2)
            label.pack()
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
    def toggle_start_menu(self):
        """Toggle start menu"""
        if hasattr(self, 'start_menu') and self.start_menu.winfo_exists():
            self.start_menu.destroy()
        else:
            self.show_start_menu()
            
    def show_start_menu(self):
        """Show start menu"""
        self.start_menu = tk.Toplevel(self.root)
        self.start_menu.title("Start Menu")
        self.start_menu.geometry("400x600+10+100")
        self.start_menu.configure(bg=self.colors["panel"])
        self.start_menu.overrideredirect(True)
        
        # Header
        header = tk.Frame(self.start_menu, bg=self.colors["accent"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        user = self.user_manager.get_current_user()
        user_name = user.username if user else "Guest"
        
        tk.Label(header, text=f"👤 {user_name}", 
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["accent"], 
                fg="#1e1e2e").pack(anchor=tk.W, padx=15, pady=15)
                
        # Apps section
        apps_frame = tk.Frame(self.start_menu, bg=self.colors["panel"])
        apps_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(apps_frame, text="Applications", 
                font=("Segoe UI", 11, "bold"),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(anchor=tk.W, pady=(0, 10))
                
        # App list
        apps = [
            ("💻 Terminal", "Command-line interface", self.open_terminal),
            ("📁 File Explorer", "Browse your files", self.open_file_explorer),
            ("📝 Text Editor", "Edit text files", self.open_text_editor),
            ("🧮 Calculator", "Basic calculations", self.open_calculator),
            ("⚙️ Settings", "System settings", self.open_settings),
            ("👥 User Manager", "Manage users", self.open_user_manager),
            ("🎮 Games", "Play games", self.open_games),
            ("📊 System Monitor", "Monitor performance", self.open_system_monitor),
            ("🌐 Web Browser", "Browse the web (simulated)", self.open_browser),
            ("🎨 Themes", "Customize appearance", self.open_themes),
        ]
        
        for icon_text, desc, cmd in apps:
            self.create_start_menu_item(apps_frame, icon_text, desc, cmd)
            
        # Power section
        power_frame = tk.Frame(self.start_menu, bg=self.colors["panel"])
        power_frame.pack(fill=tk.X, padx=10, pady=10)
        
        power_btns = [
            ("🔒 Lock", self.lock_system),
            ("🔄 Restart", self.restart_system),
            ("⏻ Shutdown", self.shutdown_system),
        ]
        
        for text, cmd in power_btns:
            btn = tk.Button(power_frame, text=text, 
                          font=("Segoe UI", 9),
                          bg=self.colors["hover"], 
                          fg=self.colors["text"],
                          relief=tk.FLAT, 
                          cursor="hand2",
                          command=cmd)
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            
    def create_start_menu_item(self, parent, icon_text, desc, command):
        """Create a start menu item"""
        item = tk.Frame(parent, bg=self.colors["panel"], cursor="hand2")
        item.pack(fill=tk.X, pady=2)
        
        # Button that fills the frame
        btn = tk.Button(item, text=icon_text, 
                       font=("Segoe UI", 10),
                       bg=self.colors["panel"], 
                       fg=self.colors["text"],
                       anchor=tk.W,
                       relief=tk.FLAT,
                       cursor="hand2",
                       command=lambda: [command(), self.start_menu.destroy()])
        btn.pack(fill=tk.X, padx=5, pady=3)
        
        # Hover effect
        def on_enter(e):
            btn.configure(bg=self.colors["hover"])
        def on_leave(e):
            btn.configure(bg=self.colors["panel"])
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
    def update_clock(self):
        """Update taskbar clock"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%m/%d/%Y")
        self.clock_label.configure(text=f"{time_str}\n{date_str}")
        self.root.after(1000, self.update_clock)
        
    # Application launchers - opens inside simulation windows
    def open_terminal(self):
        """Open terminal"""
        print("Opening Terminal...")
        self.window_manager.open_window("Terminal 💻", 900, 450, 
                                       TerminalApp,
                                       self.kernel, self.filesystem, self.user_manager)
        
    def open_file_explorer(self):
        """Open file explorer"""
        print("Opening File Explorer...")
        self.window_manager.open_window("File Explorer 📁", 700, 400,
                                       FileExplorerApp,
                                       self.filesystem)
        
    def open_text_editor(self):
        """Open text editor"""
        print("Opening Text Editor...")
        self.window_manager.open_window("Text Editor 📝", 800, 450,
                                       TextEditorApp)
        
    def open_calculator(self):
        """Open calculator"""
        print("Opening Calculator...")
        self.window_manager.open_window("Calculator 🧮", 350, 450,
                                       CalculatorApp)
        
    def open_settings(self):
        """Open settings"""
        print("Opening Settings...")
        self.window_manager.open_window("Settings ⚙️", 600, 400,
                                       SettingsApp)
        
    def open_croptopia(self):
        """Open Croptopia Enhanced"""
        print("Opening Croptopia Enhanced...")
        self.window_manager.open_window("Croptopia Enhanced 🌾", 900, 700,
                                       EnhancedCroptopia)
        
    def open_games(self):
        """Open games menu"""
        print("Opening Games Menu...")
        # Pass window_manager to games menu so it can launch games
        self.window_manager.open_window("Games 🎮", 600, 500,
                                       GamesMenuApp,
                                       self.window_manager)
        
    def open_user_manager(self):
        """User manager placeholder"""
        messagebox.showinfo("User Manager", "User management features coming soon!")
        
    def open_system_monitor(self):
        """System monitor placeholder"""
        messagebox.showinfo("System Monitor", f"Uptime: {self.kernel.get_uptime():.1f}s\nCPU: 42%")
        
    def open_browser(self):
        """Open browser"""
        from gui_apps import BrowserApp
        BrowserApp(self)
        
    def open_mail(self):
        """Open mail app"""
        messagebox.showinfo("Mail", "📧 Mail client coming soon!")
        
    def open_music(self):
        """Open music player"""
        messagebox.showinfo("Music", "🎵 Music player coming soon!")
        
    def open_photos(self):
        """Open photos app"""
        messagebox.showinfo("Photos", "🖼️ Photos app coming soon!")
        
    def open_themes(self):
        """Open theme customizer"""
        from gui_apps import ThemeApp
        ThemeApp(self)
        
    # System tray functions
    def show_volume(self):
        """Show volume control"""
        messagebox.showinfo("Volume", "🔊 Volume: 75%\n\nClick to adjust")
        
    def show_network(self):
        """Show network status"""
        messagebox.showinfo("Network", "📶 Connected\nWi-Fi: DoubOS_Network\nSignal: Strong")
        
    def show_battery(self):
        """Show battery status"""
        messagebox.showinfo("Battery", "🔋 100% - Fully Charged\nPlugged in")
        
    # Power functions
    def lock_system(self):
        """Lock the system"""
        if hasattr(self, 'start_menu'):
            self.start_menu.destroy()
        messagebox.showinfo("Lock", "🔒 System locked!\n\n(In real OS, this would show login screen)")
        
    def restart_system(self):
        """Restart the system"""
        if messagebox.askyesno("Restart", "🔄 Restart DoubOS?\n\nAll unsaved work will be lost."):
            self.root.quit()
            
    def shutdown_system(self):
        """Shutdown the system"""
        if messagebox.askyesno("Shutdown", "⏻ Shutdown DoubOS?\n\nAll unsaved work will be lost."):
            self.kernel.shutdown()
            self.root.quit()
            
    def run(self):
        """Run the desktop environment"""
        self.root.mainloop()
