"""
DoubOS GUI - Login Screen and User Registration
Beautiful login interface with user creation
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime


class LoginScreen:
    """Beautiful login screen"""
    
    def __init__(self, user_manager, filesystem):
        self.user_manager = user_manager
        self.filesystem = filesystem
        self.root = tk.Tk()
        self.root.title("DoubOS Login")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e2e")
        
        # Colors
        self.colors = {
            "bg": "#1e1e2e",
            "panel": "#313244",
            "accent": "#89b4fa",
            "text": "#cdd6f4",
            "hover": "#45475a",
            "success": "#a6e3a1",
            "danger": "#f38ba8",
        }
        
        self.logged_in_user = None
        self.time_callback_id = None  # Track the callback to cancel it later
        self.setup_ui()
        # Bind destroy event for cleanup
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def setup_ui(self):
        """Setup login UI"""
        # Background with gradient effect
        canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Gradient background
        for i in range(0, 700, 10):
            darkness = int(30 + (i / 700) * 20)
            color = f"#{darkness:02x}{darkness:02x}{2*darkness:02x}"
            canvas.create_rectangle(0, i, 1000, i+10, fill=color, outline="")
            
        # DoubOS Logo
        canvas.create_text(500, 150, text="DoubOS", 
                          font=("Segoe UI", 64, "bold"),
                          fill=self.colors["accent"])
        canvas.create_text(500, 200, text="Desktop Operating System", 
                          font=("Segoe UI", 16),
                          fill=self.colors["text"])
                          
        # Login box
        login_box = tk.Frame(self.root, bg=self.colors["panel"], 
                            width=400, height=350)
        login_box.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        login_box.pack_propagate(False)
        
        # Title
        tk.Label(login_box, text="Welcome Back!", 
                font=("Segoe UI", 20, "bold"),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(pady=(30, 10))
                
        tk.Label(login_box, text="Sign in to continue", 
                font=("Segoe UI", 10),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(pady=(0, 30))
                
        # Username field
        tk.Label(login_box, text="Username", 
                font=("Segoe UI", 10),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(anchor=tk.W, padx=40)
                
        self.username_entry = tk.Entry(login_box, 
                                      font=("Segoe UI", 12),
                                      bg=self.colors["bg"], 
                                      fg=self.colors["text"],
                                      insertbackground=self.colors["text"],
                                      relief=tk.FLAT)
        self.username_entry.pack(fill=tk.X, padx=40, pady=(5, 15))
        self.username_entry.focus()
        
        # Password field
        tk.Label(login_box, text="Password", 
                font=("Segoe UI", 10),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(anchor=tk.W, padx=40)
                
        self.password_entry = tk.Entry(login_box, 
                                      font=("Segoe UI", 12),
                                      bg=self.colors["bg"], 
                                      fg=self.colors["text"],
                                      insertbackground=self.colors["text"],
                                      relief=tk.FLAT,
                                      show="●")
        self.password_entry.pack(fill=tk.X, padx=40, pady=(5, 20))
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Login button
        login_btn = tk.Button(login_box, text="Sign In →", 
                             font=("Segoe UI", 12, "bold"),
                             bg=self.colors["accent"], 
                             fg="#1e1e2e",
                             relief=tk.FLAT, 
                             cursor="hand2",
                             command=self.login)
        login_btn.pack(fill=tk.X, padx=40, pady=(0, 10))
        
        # Register button
        register_frame = tk.Frame(login_box, bg=self.colors["panel"])
        register_frame.pack(pady=10)
        
        tk.Label(register_frame, text="Don't have an account?", 
                font=("Segoe UI", 9),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(side=tk.LEFT)
                
        register_btn = tk.Button(register_frame, text="Create one", 
                                font=("Segoe UI", 9, "bold"),
                                bg=self.colors["panel"], 
                                fg=self.colors["accent"],
                                relief=tk.FLAT, 
                                cursor="hand2",
                                command=self.show_register)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # Quick login help
        help_text = "Default users: admin/admin123, guest/guest"
        tk.Label(self.root, text=help_text, 
                font=("Segoe UI", 8),
                bg=self.colors["bg"], 
                fg=self.colors["text"]).place(relx=0.5, rely=0.95, anchor=tk.CENTER)
                
        # Time
        self.time_label = tk.Label(self.root, 
                                   font=("Segoe UI", 12),
                                   bg=self.colors["bg"], 
                                   fg=self.colors["text"])
        self.time_label.place(x=20, y=20)
        self.update_time()
        
    def update_time(self):
        """Update time display"""
        try:
            # Check if window still exists before doing anything
            if not self.root.winfo_exists():
                return
            
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            self.time_label.configure(text=f"{time_str}\n{date_str}")
            # Schedule next update
            self.time_callback_id = self.root.after(1000, self.update_time)
        except:
            pass  # Root window was destroyed, stop updating
    
    def _on_closing(self):
        """Cleanup callbacks and close the window"""
        if self.time_callback_id:
            try:
                self.root.after_cancel(self.time_callback_id)
            except:
                pass
        self.root.destroy()
        
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        if self.user_manager.login(username, password):
            self.logged_in_user = self.user_manager.get_current_user()
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.root.destroy()  # Destroy window to prevent it showing again
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
            
    def show_register(self):
        """Show registration dialog"""
        register_window = tk.Toplevel(self.root)
        register_window.title("Create Account")
        register_window.geometry("450x550")
        register_window.configure(bg=self.colors["panel"])
        register_window.resizable(False, False)
        
        # Title
        tk.Label(register_window, text="Create New Account", 
                font=("Segoe UI", 18, "bold"),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(pady=30)
                
        # Username
        tk.Label(register_window, text="Username", 
                font=("Segoe UI", 10),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(anchor=tk.W, padx=40)
                
        username_entry = tk.Entry(register_window, 
                                 font=("Segoe UI", 12),
                                 bg=self.colors["bg"], 
                                 fg=self.colors["text"],
                                 relief=tk.FLAT)
        username_entry.pack(fill=tk.X, padx=40, pady=(5, 15))
        username_entry.focus()
        
        # Password
        tk.Label(register_window, text="Password", 
                font=("Segoe UI", 10),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(anchor=tk.W, padx=40)
                
        password_entry = tk.Entry(register_window, 
                                 font=("Segoe UI", 12),
                                 bg=self.colors["bg"], 
                                 fg=self.colors["text"],
                                 relief=tk.FLAT,
                                 show="●")
        password_entry.pack(fill=tk.X, padx=40, pady=(5, 15))
        
        # Confirm password
        tk.Label(register_window, text="Confirm Password", 
                font=("Segoe UI", 10),
                bg=self.colors["panel"], 
                fg=self.colors["text"]).pack(anchor=tk.W, padx=40)
                
        confirm_entry = tk.Entry(register_window, 
                                font=("Segoe UI", 12),
                                bg=self.colors["bg"], 
                                fg=self.colors["text"],
                                relief=tk.FLAT,
                                show="●")
        confirm_entry.pack(fill=tk.X, padx=40, pady=(5, 15))
        
        # Admin checkbox
        is_admin_var = tk.BooleanVar()
        admin_check = tk.Checkbutton(register_window, 
                                    text="Create as administrator account", 
                                    variable=is_admin_var,
                                    font=("Segoe UI", 9),
                                    bg=self.colors["panel"], 
                                    fg=self.colors["text"],
                                    selectcolor=self.colors["bg"],
                                    activebackground=self.colors["panel"],
                                    activeforeground=self.colors["text"])
        admin_check.pack(pady=10)
        
        # Create button
        def create_account():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill all fields")
                return
                
            if len(username) < 3:
                messagebox.showerror("Error", "Username must be at least 3 characters")
                return
                
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
                
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
                
            if self.user_manager.add_user(username, password, is_admin_var.get()):
                messagebox.showinfo("Success", 
                    f"Account created successfully!\n\nUsername: {username}\n" +
                    f"Type: {'Administrator' if is_admin_var.get() else 'Standard User'}\n\n" +
                    "You can now log in with your new account.")
                register_window.destroy()
            else:
                messagebox.showerror("Error", "Username already exists")
                
        create_btn = tk.Button(register_window, text="Create Account", 
                              font=("Segoe UI", 12, "bold"),
                              bg=self.colors["success"], 
                              fg="#1e1e2e",
                              relief=tk.FLAT, 
                              cursor="hand2",
                              command=create_account)
        create_btn.pack(fill=tk.X, padx=40, pady=20)
        
        # Info
        info = "ℹ️ Choose a strong password to keep your account secure"
        tk.Label(register_window, text=info, 
                font=("Segoe UI", 8),
                bg=self.colors["panel"], 
                fg=self.colors["text"],
                wraplength=350).pack(pady=10)
                
    def run(self):
        """Run login screen"""
        try:
            self.root.mainloop()
        finally:
            # Ensure cleanup happens even if mainloop exits abnormally
            self._on_closing_silent()
        return self.logged_in_user
    
    def _on_closing_silent(self):
        """Silent cleanup without destroying (root may already be destroyed)"""
        if self.time_callback_id:
            try:
                self.root.after_cancel(self.time_callback_id)
                self.time_callback_id = None
            except:
                pass
