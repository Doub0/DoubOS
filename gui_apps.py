"""
DoubOS GUI Applications
All graphical applications for the desktop environment
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
from datetime import datetime
import os
import random


class BaseWindow:
    """Base class for all GUI windows"""
    
    def __init__(self, desktop, title, width=800, height=600, icon="🪟"):
        self.desktop = desktop
        self.window = tk.Toplevel(desktop.root)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}+{desktop.next_window_offset}+{desktop.next_window_offset}")
        desktop.next_window_offset = (desktop.next_window_offset + 30) % 200
        self.window.configure(bg=desktop.colors["panel"])
        
        # Title bar
        self.create_title_bar(title, icon)
        
        # Content area
        self.content = tk.Frame(self.window, bg=desktop.colors["bg"])
        self.content.pack(fill=tk.BOTH, expand=True)
        
    def create_title_bar(self, title, icon):
        """Create custom title bar"""
        titlebar = tk.Frame(self.window, bg=self.desktop.colors["accent"], height=35)
        titlebar.pack(fill=tk.X)
        titlebar.pack_propagate(False)
        
        # Title
        tk.Label(titlebar, text=f"{icon} {title}", 
                font=("Segoe UI", 10, "bold"),
                bg=self.desktop.colors["accent"], 
                fg="#1e1e2e").pack(side=tk.LEFT, padx=10)
                
        # Close button
        close_btn = tk.Button(titlebar, text="✕", 
                             font=("Segoe UI", 12, "bold"),
                             bg=self.desktop.colors["danger"], 
                             fg="white",
                             relief=tk.FLAT, 
                             cursor="hand2",
                             command=self.window.destroy,
                             width=3)
        close_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Minimize button
        min_btn = tk.Button(titlebar, text="−", 
                           font=("Segoe UI", 12, "bold"),
                           bg=self.desktop.colors["warning"], 
                           fg="#1e1e2e",
                           relief=tk.FLAT, 
                           cursor="hand2",
                           command=self.window.iconify,
                           width=3)
        min_btn.pack(side=tk.RIGHT, padx=2, pady=2)


class TerminalApp(BaseWindow):
    """Terminal application"""
    
    def __init__(self, desktop, kernel, filesystem, user_manager):
        super().__init__(desktop, "Terminal", 900, 600, "💻")
        self.kernel = kernel
        self.filesystem = filesystem
        self.user_manager = user_manager
        self.current_dir = "/"
        
        # Import command processor
        from commands import CommandProcessor, CommandContext
        from dangerous_commands import register_dangerous_commands
        from utilities import register_utility_commands
        from fun_commands import register_fun_commands
        
        shell_mock = type('obj', (object,), {'current_dir': '/', 'change_directory': lambda x: None})()
        context = CommandContext(kernel, filesystem, user_manager, shell_mock)
        self.processor = CommandProcessor(context)
        register_dangerous_commands(self.processor)
        register_utility_commands(self.processor)
        register_fun_commands(self.processor)
        context.commands = self.processor.commands
        context.current_dir = "/"
        
        self.setup_ui()
        self.print_welcome()
        
    def setup_ui(self):
        """Setup terminal UI"""
        # Output area
        self.output = scrolledtext.ScrolledText(
            self.content, 
            bg="#1e1e2e", 
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = tk.Frame(self.content, bg=self.desktop.colors["panel"])
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Prompt label
        user = self.user_manager.get_current_user()
        username = user.username if user else "guest"
        self.prompt_text = f"{username}@DoubOS:~$ "
        
        self.prompt_label = tk.Label(input_frame, text=self.prompt_text,
                                     bg=self.desktop.colors["panel"],
                                     fg=self.desktop.colors["success"],
                                     font=("Consolas", 10, "bold"))
        self.prompt_label.pack(side=tk.LEFT)
        
        # Input field
        self.input = tk.Entry(input_frame, bg=self.desktop.colors["hover"],
                             fg=self.desktop.colors["text"],
                             insertbackground=self.desktop.colors["text"],
                             font=("Consolas", 10),
                             relief=tk.FLAT)
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input.bind("<Return>", self.execute_command)
        self.input.focus()
        
    def print_welcome(self):
        """Print welcome message"""
        welcome = """DoubOS Terminal v1.0
Type 'help' for available commands.

"""
        self.output.insert(tk.END, welcome)
        
    def execute_command(self, event=None):
        """Execute command"""
        command = self.input.get().strip()
        if not command:
            return
            
        # Echo command
        self.output.insert(tk.END, f"{self.prompt_text}{command}\n", "input")
        self.output.tag_config("input", foreground="#a6e3a1")
        
        # Execute
        result = self.processor.execute(command)
        if result:
            self.output.insert(tk.END, result + "\n\n")
        else:
            self.output.insert(tk.END, "\n")
            
        self.output.see(tk.END)
        self.input.delete(0, tk.END)
        
        # Check if shutdown
        if not self.kernel.running:
            self.window.destroy()


class FileExplorerApp(BaseWindow):
    """File explorer application"""
    
    def __init__(self, desktop, filesystem, user_manager):
        super().__init__(desktop, "File Explorer", 900, 650, "📁")
        self.filesystem = filesystem
        self.user_manager = user_manager
        self.current_path = "/"
        self.setup_ui()
        self.refresh()
        
    def setup_ui(self):
        """Setup file explorer UI"""
        # Toolbar
        toolbar = tk.Frame(self.content, bg=self.desktop.colors["panel"], height=50)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        toolbar.pack_propagate(False)
        
        # Navigation buttons
        tk.Button(toolbar, text="⬅️", font=("Segoe UI", 12),
                 bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"],
                 relief=tk.FLAT, cursor="hand2",
                 command=self.go_up).pack(side=tk.LEFT, padx=2)
                 
        tk.Button(toolbar, text="🏠", font=("Segoe UI", 12),
                 bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"],
                 relief=tk.FLAT, cursor="hand2",
                 command=self.go_home).pack(side=tk.LEFT, padx=2)
                 
        tk.Button(toolbar, text="🔄", font=("Segoe UI", 12),
                 bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"],
                 relief=tk.FLAT, cursor="hand2",
                 command=self.refresh).pack(side=tk.LEFT, padx=2)
                 
        # Address bar
        self.address_bar = tk.Entry(toolbar, bg=self.desktop.colors["hover"],
                                    fg=self.desktop.colors["text"],
                                    font=("Segoe UI", 10))
        self.address_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.address_bar.bind("<Return>", lambda e: self.navigate_to(self.address_bar.get()))
        
        # Action buttons
        tk.Button(toolbar, text="➕ New", font=("Segoe UI", 9),
                 bg=self.desktop.colors["success"], fg="#1e1e2e",
                 relief=tk.FLAT, cursor="hand2",
                 command=self.new_file).pack(side=tk.RIGHT, padx=2)
                 
        # File list
        list_frame = tk.Frame(self.content, bg=self.desktop.colors["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.file_list = tk.Listbox(list_frame, bg=self.desktop.colors["hover"],
                                    fg=self.desktop.colors["text"],
                                    font=("Segoe UI", 10),
                                    selectmode=tk.SINGLE,
                                    yscrollcommand=scrollbar.set,
                                    relief=tk.FLAT)
        self.file_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_list.yview)
        
        self.file_list.bind("<Double-Button-1>", self.open_item)
        self.file_list.bind("<Button-3>", self.show_context_menu)
        
    def refresh(self):
        """Refresh file list"""
        self.file_list.delete(0, tk.END)
        self.address_bar.delete(0, tk.END)
        self.address_bar.insert(0, self.current_path)
        
        items = self.filesystem.list_directory(self.current_path)
        if items:
            # Sort: directories first, then files
            dirs = sorted([i for i in items if i.is_directory], key=lambda x: x.name)
            files = sorted([i for i in items if not i.is_directory], key=lambda x: x.name)
            
            for item in dirs:
                self.file_list.insert(tk.END, f"📁 {item.name}/")
                
            for item in files:
                icon = self.get_file_icon(item.name)
                self.file_list.insert(tk.END, f"{icon} {item.name}")
                
    def get_file_icon(self, filename):
        """Get icon for file type"""
        ext = os.path.splitext(filename)[1].lower()
        icons = {
            '.txt': '📝',
            '.py': '🐍',
            '.json': '📋',
            '.md': '📄',
            '.log': '📊',
        }
        return icons.get(ext, '📄')
        
    def open_item(self, event=None):
        """Open selected item"""
        selection = self.file_list.curselection()
        if not selection:
            return
            
        item_text = self.file_list.get(selection[0])
        # Remove icon and trailing /
        name = item_text.split(' ', 1)[1].rstrip('/')
        
        new_path = self.current_path.rstrip('/') + '/' + name
        
        if self.filesystem.is_directory(new_path):
            self.current_path = new_path
            self.refresh()
        else:
            # Open file in text editor
            content = self.filesystem.read_file(new_path)
            if content is not None:
                self.show_file_viewer(name, content)
                
    def show_file_viewer(self, filename, content):
        """Show file content"""
        viewer = tk.Toplevel(self.window)
        viewer.title(f"View: {filename}")
        viewer.geometry("700x500")
        viewer.configure(bg=self.desktop.colors["bg"])
        
        text = scrolledtext.ScrolledText(viewer, bg=self.desktop.colors["hover"],
                                        fg=self.desktop.colors["text"],
                                        font=("Consolas", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(1.0, content)
        
    def navigate_to(self, path):
        """Navigate to path"""
        if self.filesystem.is_directory(path):
            self.current_path = path
            self.refresh()
        else:
            messagebox.showerror("Error", f"'{path}' is not a directory")
            
    def go_up(self):
        """Go to parent directory"""
        if self.current_path == "/":
            return
        parts = self.current_path.rstrip('/').split('/')
        self.current_path = '/'.join(parts[:-1]) or '/'
        self.refresh()
        
    def go_home(self):
        """Go to home directory"""
        user = self.user_manager.get_current_user()
        self.current_path = user.home_dir if user else "/home"
        self.refresh()
        
    def new_file(self):
        """Create new file or folder"""
        choice = messagebox.askquestion("New", "Create a folder?\n(No = create file)")
        name = simpledialog.askstring("New", "Enter name:")
        if not name:
            return
            
        path = self.current_path.rstrip('/') + '/' + name
        user = self.user_manager.get_current_user()
        owner = user.username if user else "guest"
        
        if choice == 'yes':
            self.filesystem.mkdir(path, owner=owner)
        else:
            self.filesystem.write_file(path, "", owner)
            
        self.refresh()
        
    def show_context_menu(self, event):
        """Show right-click context menu"""
        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="📝 Open", command=self.open_item)
        menu.add_command(label="✏️ Rename", command=self.rename_item)
        menu.add_command(label="🗑️ Delete", command=self.delete_item)
        menu.post(event.x_root, event.y_root)
        
    def rename_item(self):
        """Rename selected item"""
        messagebox.showinfo("Rename", "Rename feature coming soon!")
        
    def delete_item(self):
        """Delete selected item"""
        selection = self.file_list.curselection()
        if not selection:
            return
            
        item_text = self.file_list.get(selection[0])
        name = item_text.split(' ', 1)[1].rstrip('/')
        
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            path = self.current_path.rstrip('/') + '/' + name
            self.filesystem.remove(path, recursive=True)
            self.refresh()


class TextEditorApp(BaseWindow):
    """Simple text editor"""
    
    def __init__(self, desktop, filesystem):
        super().__init__(desktop, "Text Editor", 800, 600, "📝")
        self.filesystem = filesystem
        self.current_file = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup text editor UI"""
        # Menu bar
        menubar = tk.Frame(self.content, bg=self.desktop.colors["panel"], height=40)
        menubar.pack(fill=tk.X)
        menubar.pack_propagate(False)
        
        buttons = [
            ("📄 New", self.new_file),
            ("📁 Open", self.open_file),
            ("💾 Save", self.save_file),
            ("💾 Save As", self.save_as),
        ]
        
        for text, cmd in buttons:
            tk.Button(menubar, text=text, font=("Segoe UI", 9),
                     bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"],
                     relief=tk.FLAT, cursor="hand2",
                     command=cmd).pack(side=tk.LEFT, padx=5, pady=5)
                     
        # Text area
        self.text = scrolledtext.ScrolledText(
            self.content,
            bg="#1e1e2e",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            font=("Consolas", 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def new_file(self):
        """Create new file"""
        if messagebox.askyesno("New", "Clear current content?"):
            self.text.delete(1.0, tk.END)
            self.current_file = None
            
    def open_file(self):
        """Open file (simplified - just ask for path)"""
        path = simpledialog.askstring("Open", "Enter file path:")
        if not path:
            return
            
        content = self.filesystem.read_file(path)
        if content is not None:
            self.text.delete(1.0, tk.END)
            self.text.insert(1.0, content)
            self.current_file = path
        else:
            messagebox.showerror("Error", f"Could not open '{path}'")
            
    def save_file(self):
        """Save file"""
        if self.current_file:
            content = self.text.get(1.0, tk.END)
            self.filesystem.write_file(self.current_file, content)
            messagebox.showinfo("Saved", f"Saved to {self.current_file}")
        else:
            self.save_as()
            
    def save_as(self):
        """Save file as"""
        path = simpledialog.askstring("Save As", "Enter file path:")
        if not path:
            return
            
        content = self.text.get(1.0, tk.END)
        if self.filesystem.write_file(path, content):
            self.current_file = path
            messagebox.showinfo("Saved", f"Saved to {path}")
        else:
            messagebox.showerror("Error", "Could not save file")


class CalculatorApp(BaseWindow):
    """Simple calculator"""
    
    def __init__(self, desktop):
        super().__init__(desktop, "Calculator", 350, 500, "🧮")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup calculator UI"""
        # Display
        self.display = tk.Entry(self.content, font=("Segoe UI", 24),
                               bg=self.desktop.colors["hover"],
                               fg=self.desktop.colors["text"],
                               justify=tk.RIGHT,
                               relief=tk.FLAT)
        self.display.pack(fill=tk.X, padx=10, pady=10)
        
        # Buttons
        buttons_frame = tk.Frame(self.content, bg=self.desktop.colors["bg"])
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        buttons = [
            ['C', '(', ')', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', '←']
        ]
        
        for row in buttons:
            row_frame = tk.Frame(buttons_frame, bg=self.desktop.colors["bg"])
            row_frame.pack(fill=tk.BOTH, expand=True)
            
            for btn_text in row:
                color = self.desktop.colors["accent"] if btn_text in ['=', 'C'] else self.desktop.colors["hover"]
                fg = "#1e1e2e" if btn_text in ['=', 'C'] else self.desktop.colors["text"]
                
                btn = tk.Button(row_frame, text=btn_text,
                               font=("Segoe UI", 18, "bold"),
                               bg=color, fg=fg,
                               relief=tk.FLAT, cursor="hand2",
                               command=lambda t=btn_text: self.button_click(t))
                btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
                
    def button_click(self, char):
        """Handle button click"""
        if char == '=':
            try:
                result = eval(self.display.get())
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
        elif char == 'C':
            self.display.delete(0, tk.END)
        elif char == '←':
            current = self.display.get()
            self.display.delete(0, tk.END)
            self.display.insert(0, current[:-1])
        else:
            self.display.insert(tk.END, char)


class SettingsApp(BaseWindow):
    """System settings"""
    
    def __init__(self, desktop, user_manager, filesystem):
        super().__init__(desktop, "Settings", 700, 600, "⚙️")
        self.user_manager = user_manager
        self.filesystem = filesystem
        self.setup_ui()
        
    def setup_ui(self):
        """Setup settings UI"""
        # Sidebar
        sidebar = tk.Frame(self.content, bg=self.desktop.colors["panel"], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="Settings", font=("Segoe UI", 14, "bold"),
                bg=self.desktop.colors["panel"], fg=self.desktop.colors["text"]).pack(pady=20)
                
        categories = [
            ("👤 Account", self.show_account),
            ("🎨 Appearance", self.show_appearance),
            ("🔔 Notifications", self.show_notifications),
            ("📊 System", self.show_system),
            ("ℹ️ About", self.show_about),
        ]
        
        for text, cmd in categories:
            btn = tk.Button(sidebar, text=text, font=("Segoe UI", 10),
                           bg=self.desktop.colors["panel"], fg=self.desktop.colors["text"],
                           anchor=tk.W, relief=tk.FLAT, cursor="hand2",
                           command=cmd)
            btn.pack(fill=tk.X, padx=10, pady=2)
            
        # Content area
        self.settings_content = tk.Frame(self.content, bg=self.desktop.colors["bg"])
        self.settings_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.show_about()
        
    def clear_content(self):
        """Clear settings content area"""
        for widget in self.settings_content.winfo_children():
            widget.destroy()
            
    def show_account(self):
        """Show account settings"""
        self.clear_content()
        tk.Label(self.settings_content, text="Account Settings",
                font=("Segoe UI", 16, "bold"),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(anchor=tk.W, pady=(0, 20))
                
        user = self.user_manager.get_current_user()
        if user:
            info = f"""Username: {user.username}
UID: {user.uid}
Home: {user.home_dir}
Role: {'Admin' if user.is_admin else 'User'}
Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'}
"""
            tk.Label(self.settings_content, text=info, font=("Segoe UI", 10),
                    bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"],
                    justify=tk.LEFT).pack(anchor=tk.W)
                    
    def show_appearance(self):
        """Show appearance settings"""
        self.clear_content()
        tk.Label(self.settings_content, text="Appearance",
                font=("Segoe UI", 16, "bold"),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(anchor=tk.W, pady=(0, 20))
                
        tk.Label(self.settings_content, text="Theme customization coming soon!",
                font=("Segoe UI", 10),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack()
                
    def show_notifications(self):
        """Show notification settings"""
        self.clear_content()
        tk.Label(self.settings_content, text="Notifications",
                font=("Segoe UI", 16, "bold"),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(anchor=tk.W, pady=(0, 20))
                
        tk.Checkbutton(self.settings_content, text="Enable notifications",
                      bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"],
                      selectcolor=self.desktop.colors["hover"],
                      font=("Segoe UI", 10)).pack(anchor=tk.W)
                      
    def show_system(self):
        """Show system info"""
        self.clear_content()
        tk.Label(self.settings_content, text="System Information",
                font=("Segoe UI", 16, "bold"),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(anchor=tk.W, pady=(0, 20))
                
        info = f"""OS: DoubOS 1.0
Kernel: Virtual
Uptime: {self.desktop.kernel.get_uptime()}
Users: {len(self.user_manager.users)}
"""
        tk.Label(self.settings_content, text=info, font=("Segoe UI", 10),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"],
                justify=tk.LEFT).pack(anchor=tk.W)
                
    def show_about(self):
        """Show about info"""
        self.clear_content()
        tk.Label(self.settings_content, text="About DoubOS",
                font=("Segoe UI", 16, "bold"),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(anchor=tk.W, pady=(0, 20))
                
        about = """DoubOS Desktop Environment
Version 1.0

A fully-fledged operating system simulator
with graphical user interface.

Features:
• Virtual file system
• User management
• 50+ terminal commands
• Graphical applications
• Bootable USB support
• Linux-grade architecture

Created for learning and experimentation.
"""
        tk.Label(self.settings_content, text=about, font=("Segoe UI", 10),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"],
                justify=tk.LEFT).pack(anchor=tk.W)


# Additional app classes to be continued...
class UserManagerApp(BaseWindow):
    """User management app"""
    
    def __init__(self, desktop, user_manager):
        super().__init__(desktop, "User Manager", 600, 500, "👥")
        self.user_manager = user_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI"""
        tk.Label(self.content, text="User Manager - Create, edit, delete users",
                font=("Segoe UI", 12),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(pady=20)
                
        # Add user button
        tk.Button(self.content, text="➕ Add New User",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.desktop.colors["success"], fg="#1e1e2e",
                 relief=tk.FLAT, cursor="hand2",
                 command=self.add_user).pack(pady=10)
                 
        # User list
        self.refresh_users()
        
    def refresh_users(self):
        """Refresh user list"""
        # Clear existing
        for widget in self.content.winfo_children()[2:]:
            widget.destroy()
            
        for user in self.user_manager.list_users():
            frame = tk.Frame(self.content, bg=self.desktop.colors["hover"])
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            role = "👑 Admin" if user.is_admin else "👤 User"
            tk.Label(frame, text=f"{role} - {user.username}",
                    font=("Segoe UI", 10),
                    bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"]).pack(side=tk.LEFT, padx=10)
                    
            if user.username != "root":
                tk.Button(frame, text="🗑️",
                         bg=self.desktop.colors["danger"], fg="white",
                         relief=tk.FLAT, cursor="hand2",
                         command=lambda u=user.username: self.delete_user(u)).pack(side=tk.RIGHT, padx=5)
                         
    def add_user(self):
        """Add new user"""
        username = simpledialog.askstring("New User", "Enter username:")
        if not username:
            return
            
        password = simpledialog.askstring("New User", "Enter password:", show='*')
        if not password:
            return
            
        is_admin = messagebox.askyesno("New User", "Make this user an admin?")
        
        if self.user_manager.add_user(username, password, is_admin):
            messagebox.showinfo("Success", f"User '{username}' created!")
            self.refresh_users()
        else:
            messagebox.showerror("Error", "User already exists!")
            
    def delete_user(self, username):
        """Delete user"""
        if messagebox.askyesno("Delete", f"Delete user '{username}'?"):
            if self.user_manager.remove_user(username):
                messagebox.showinfo("Success", f"User '{username}' deleted!")
                self.refresh_users()


class GamesApp(BaseWindow):
    """Simple games"""
    
    def __init__(self, desktop):
        super().__init__(desktop, "Games", 400, 500, "🎮")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup games UI"""
        tk.Label(self.content, text="Mini Games",
                font=("Segoe UI", 16, "bold"),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(pady=20)
                
        games = [
            ("🎲 Dice Roller", self.dice_game),
            ("🪙 Coin Flip", self.coin_game),
            ("🎯 Number Guess", self.guess_game),
            ("🎰 Random Fortune", self.fortune_game),
        ]
        
        for text, cmd in games:
            tk.Button(self.content, text=text,
                     font=("Segoe UI", 12),
                     bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"],
                     relief=tk.FLAT, cursor="hand2",
                     command=cmd,
                     width=20).pack(pady=10)
                     
    def dice_game(self):
        """Roll dice"""
        result = random.randint(1, 6)
        messagebox.showinfo("Dice Roll", f"🎲 You rolled: {result}")
        
    def coin_game(self):
        """Flip coin"""
        result = random.choice(["Heads", "Tails"])
        messagebox.showinfo("Coin Flip", f"🪙 {result}!")
        
    def guess_game(self):
        """Number guessing game"""
        number = random.randint(1, 100)
        guess = simpledialog.askinteger("Guess", "Guess a number (1-100):")
        if guess == number:
            messagebox.showinfo("Winner!", f"🎉 Correct! The number was {number}")
        else:
            messagebox.showinfo("Try Again", f"❌ Wrong! It was {number}")
            
    def fortune_game(self):
        """Random fortune"""
        fortunes = [
            "You will write bug-free code today!",
            "A great opportunity awaits...",
            "Your next commit will be legendary!",
            "Success is in your future!",
            "Keep coding, great things are coming!",
        ]
        messagebox.showinfo("Fortune", f"🔮 {random.choice(fortunes)}")


class SystemMonitorApp(BaseWindow):
    """System monitor"""
    
    def __init__(self, desktop, kernel):
        super().__init__(desktop, "System Monitor", 600, 400, "📊")
        self.kernel = kernel
        self.setup_ui()
        self.update_stats()
        
    def setup_ui(self):
        """Setup UI"""
        self.stats_label = tk.Label(self.content, font=("Consolas", 11),
                                    bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"],
                                    justify=tk.LEFT)
        self.stats_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def update_stats(self):
        """Update system stats"""
        stats = f"""DoubOS System Monitor

Uptime: {self.kernel.get_uptime()}
Version: {self.kernel.version}

Processes: 2 running
Memory: Virtual (unlimited)
CPU: Simulated

Command History: {len(self.kernel.command_history)} commands
Environment Variables: {len(self.kernel.environment_vars)}

Status: ✅ All systems operational
"""
        self.stats_label.configure(text=stats)
        self.window.after(1000, self.update_stats)


class BrowserApp(BaseWindow):
    """Simple web browser simulator"""
    
    def __init__(self, desktop):
        super().__init__(desktop, "Web Browser", 900, 700, "🌐")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup browser UI"""
        # Address bar
        toolbar = tk.Frame(self.content, bg=self.desktop.colors["panel"], height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        tk.Button(toolbar, text="⬅️", font=("Segoe UI", 12),
                 bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(toolbar, text="➡️", font=("Segoe UI", 12),
                 bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"],
                 relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
                 
        address = tk.Entry(toolbar, font=("Segoe UI", 10),
                          bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"])
        address.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        address.insert(0, "https://doubos.local/")
        
        # Content
        content_html = """
        <html>
        <body style="background: #1e1e2e; color: #cdd6f4; font-family: sans-serif; padding: 40px;">
            <h1 style="color: #89b4fa;">Welcome to DoubOS Browser!</h1>
            <p>This is a simulated web browser.</p>
            <p>In a real implementation, this would render actual web pages.</p>
            <hr>
            <h2>Quick Links:</h2>
            <ul>
                <li>DoubOS Homepage</li>
                <li>Documentation</li>
                <li>Community Forums</li>
                <li>App Store</li>
            </ul>
        </body>
        </html>
        """
        
        text = scrolledtext.ScrolledText(self.content, bg="#1e1e2e", fg="#cdd6f4",
                                        font=("Segoe UI", 10), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text.insert(1.0, "🌐 DoubOS Browser - Simulated\n\n" + 
                   "Visit: https://doubos.local/\n\n" +
                   "This browser simulates web browsing.\n" +
                   "Full web rendering would require additional libraries.")


class ThemeApp(BaseWindow):
    """Theme customizer"""
    
    def __init__(self, desktop):
        super().__init__(desktop, "Themes", 500, 400, "🎨")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup theme UI"""
        tk.Label(self.content, text="Theme Customization",
                font=("Segoe UI", 14, "bold"),
                bg=self.desktop.colors["bg"], fg=self.desktop.colors["text"]).pack(pady=20)
                
        themes = [
            ("🌙 Dark (Current)", "#1e1e2e"),
            ("☀️ Light", "#ffffff"),
            ("🌊 Ocean", "#1a5490"),
            ("🌲 Forest", "#2d5016"),
            ("🌸 Sakura", "#ff69b4"),
        ]
        
        for name, color in themes:
            frame = tk.Frame(self.content, bg=self.desktop.colors["hover"])
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            color_box = tk.Frame(frame, bg=color, width=30, height=30)
            color_box.pack(side=tk.LEFT, padx=10)
            color_box.pack_propagate(False)
            
            tk.Label(frame, text=name, font=("Segoe UI", 10),
                    bg=self.desktop.colors["hover"], fg=self.desktop.colors["text"]).pack(side=tk.LEFT)
