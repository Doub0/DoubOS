"""
DoubOS Window Manager
Manage windows inside the desktop simulation
"""

import tkinter as tk
from tkinter import ttk
import time


class SimulationWindow:
    """A window that opens inside the desktop simulation"""
    
    def __init__(self, parent_frame, title, width, height, app_class, *args, x_pos=50, y_pos=50, **kwargs):
        """Create a simulation window"""
        self.parent_frame = parent_frame
        self.title = title
        self.width = width
        self.height = height
        self.app_class = app_class
        self.app_args = args
        self.app_kwargs = kwargs
        self.is_minimized = False
        self.is_maximized = False
        self.original_geometry = None
        self.x_pos = x_pos
        self.y_pos = y_pos
        
        # Create outer window frame with border and shadow effect
        self.window_frame = tk.Frame(parent_frame, bg="#000000", relief=tk.RAISED, bd=0)
        self.window_frame.place(x=self.x_pos, y=self.y_pos, width=width, height=height)
        
        # Add inner border for depth
        self.inner_border = tk.Frame(self.window_frame, bg="#313244", relief=tk.RIDGE, bd=2)
        self.inner_border.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Title bar
        self.titlebar = tk.Frame(self.inner_border, bg="#45475a", height=32)
        self.titlebar.pack(side=tk.TOP, fill=tk.X)
        self.titlebar.pack_propagate(False)
        
        # Title text
        tk.Label(self.titlebar, text=f"  {title}", 
                bg="#45475a", fg="#cdd6f4", 
                font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Control buttons frame
        buttons_frame = tk.Frame(self.titlebar, bg="#45475a")
        buttons_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Minimize button
        self.minimize_btn = tk.Button(buttons_frame, text="−", 
                                     bg="#f9e2af", fg="#1e1e2e",
                                     font=("Arial", 10, "bold"),
                                     command=self.minimize,
                                     bd=0, width=2, height=1, cursor="hand2")
        self.minimize_btn.pack(side=tk.LEFT, padx=2)
        
        # Maximize button
        self.maximize_btn = tk.Button(buttons_frame, text="□", 
                                     bg="#89b4fa", fg="#1e1e2e",
                                     font=("Arial", 10, "bold"),
                                     command=self.toggle_maximize,
                                     bd=0, width=2, height=1, cursor="hand2")
        self.maximize_btn.pack(side=tk.LEFT, padx=2)
        
        # Close button
        self.close_btn = tk.Button(buttons_frame, text="✕", 
                                  bg="#f38ba8", fg="white",
                                  font=("Arial", 10, "bold"),
                                  command=self.close,
                                  bd=0, width=2, height=1, cursor="hand2")
        self.close_btn.pack(side=tk.LEFT, padx=2)
        
        # Content frame
        self.content_frame = tk.Frame(self.inner_border, bg="#1e1e2e")
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Make window draggable
        self.drag_data = {"x": 0, "y": 0}
        self.titlebar.bind("<Button-1>", self.start_drag)
        self.titlebar.bind("<B1-Motion>", self.do_drag)
        
        # Create the app inside this window
        self.create_app()
        
        # Bring to front
        self.window_frame.lift()
        
    def create_app(self):
        """Create the application inside this window"""
        try:
            print(f"Creating app: {self.app_class.__name__}")
            self.app = self.app_class(self.content_frame, *self.app_args, **self.app_kwargs)
            self.app.pack(fill=tk.BOTH, expand=True)
            print(f"✓ App created successfully")
        except Exception as e:
            # If app fails, show error
            import traceback
            print(f"✗ Error loading app: {e}")
            traceback.print_exc()
            error_label = tk.Label(self.content_frame, 
                                  text=f"Error loading app:\n{str(e)}",
                                  bg="#1e1e2e", fg="#f38ba8",
                                  font=("Segoe UI", 10))
            error_label.pack(expand=True)
            
    def start_drag(self, event):
        """Start window drag"""
        self.drag_data["x"] = event.x_root - self.window_frame.winfo_x()
        self.drag_data["y"] = event.y_root - self.window_frame.winfo_y()
        
    def do_drag(self, event):
        """Perform window drag"""
        if not self.is_maximized:
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.window_frame.place(x=x, y=y, width=self.width, height=self.height)
            
    def minimize(self):
        """Minimize window"""
        if self.is_minimized:
            # Restore
            self.window_frame.place(x=50, y=50, width=self.width, height=self.height)
            self.minimize_btn.configure(text="_")
            self.is_minimized = False
        else:
            # Minimize to taskbar
            self.window_frame.place(x=0, y=0, width=200, height=30)
            self.minimize_btn.configure(text="▢")
            self.is_minimized = True
            
    def toggle_maximize(self):
        """Maximize/restore window"""
        if self.is_maximized:
            # Restore
            self.window_frame.place(x=50, y=50, width=self.width, height=self.height)
            self.is_maximized = False
        else:
            # Maximize
            self.original_geometry = (50, 50, self.width, self.height)
            self.window_frame.place(x=0, y=0, relwidth=1, relheight=1)
            self.is_maximized = True
            
    def close(self):
        """Close window"""
        # Call cleanup methods if available
        if hasattr(self, 'app'):
            if hasattr(self.app, 'on_destroy'):
                try:
                    self.app.on_destroy()
                except:
                    pass
            if hasattr(self.app, 'cleanup'):
                try:
                    self.app.cleanup()
                except:
                    pass
            if hasattr(self.app, '_on_destroy'):
                try:
                    self.app._on_destroy()
                except:
                    pass
        
        # Destroy the window frame
        try:
            self.window_frame.destroy()
        except:
            pass
            
    def focus(self):
        """Bring window to front"""
        self.window_frame.lift()


class WindowManager:
    """Manage all windows in the simulation"""
    
    def __init__(self, desktop_frame):
        self.desktop_frame = desktop_frame
        self.windows = []
        self.z_order = 0
        self.window_offset = 0
        
    def open_window(self, title, width, height, app_class, *args, **kwargs):
        """Open a new window in the simulation"""
        # Calculate staggered position
        offset = (self.window_offset * 30) % 200
        x_pos = 50 + offset
        y_pos = 50 + offset
        
        window = SimulationWindow(self.desktop_frame, title, width, height, 
                                 app_class, *args, x_pos=x_pos, y_pos=y_pos, **kwargs)
        self.windows.append(window)
        window.focus()
        self.window_offset += 1
        print(f"✓ Window opened at ({x_pos}, {y_pos})")
        return window
        
    def close_window(self, window):
        """Close a window"""
        if window in self.windows:
            self.windows.remove(window)
            window.close()
            
    def close_all(self):
        """Close all windows"""
        for window in list(self.windows):
            window.close()
        self.windows.clear()
