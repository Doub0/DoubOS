# DoubOS Window System - Technical Guide

## 🪟 Window Architecture

### Design Philosophy
DoubOS uses **frame-based windows** that open **INSIDE** the desktop simulation, not as separate operating system windows. This creates a true desktop environment simulation.

---

## 🏗️ Architecture Overview

### Component Hierarchy
```
DoubOS Desktop
└── Root Tk Window (1200x800)
    ├── Desktop Frame (background layer)
    │   ├── Wallpaper Canvas (placed)
    │   ├── Desktop Icons (placed at specific x,y)
    │   └── Simulation Windows (managed by WindowManager)
    │       ├── Outer Frame (border + shadow)
    │       ├── Inner Border Frame
    │       │   ├── Title Bar (32px height)
    │       │   │   ├── Title Text
    │       │   │   └── Control Buttons (−, □, ✕)
    │       │   └── Content Frame
    │       │       └── Application (Terminal, Files, etc.)
    └── Taskbar (50px height, bottom)
```

---

## 🔧 Window Manager System

### `window_manager.py`

#### **WindowManager Class**
Manages all windows in the simulation.

**Properties:**
- `desktop_frame` - Parent frame where windows are placed
- `windows` - List of all open SimulationWindow instances
- `window_offset` - Counter for staggered window positioning

**Methods:**
```python
open_window(title, width, height, app_class, *args, **kwargs)
    # Opens a new window with specified app
    # Returns: SimulationWindow instance
    
close_window(window)
    # Closes a specific window
    
close_all()
    # Closes all windows
```

**Window Positioning:**
- Windows are staggered by 30px increments
- Offset cycles every 200px to stay on screen
- Formula: `position = 50 + (offset * 30) % 200`

---

#### **SimulationWindow Class**
Individual window inside the simulation.

**Properties:**
- `parent_frame` - Desktop frame where window lives
- `window_frame` - Outer frame (with shadow/border)
- `inner_border` - Inner frame (for depth effect)
- `titlebar` - Top bar with title and controls
- `content_frame` - Where the app is rendered
- `is_minimized` - Minimized state
- `is_maximized` - Maximized state
- `x_pos, y_pos` - Window position

**Methods:**
```python
create_app()
    # Instantiates the app class inside content_frame
    
start_drag(event) / do_drag(event)
    # Handle window dragging
    
minimize()
    # Minimize/restore window
    
toggle_maximize()
    # Maximize/restore window
    
close()
    # Close and cleanup window
    
focus()
    # Bring window to front (z-order)
```

---

## 🎨 Visual Design

### Window Styling

**Outer Frame:**
- Background: #000000 (black shadow effect)
- Border: 0px
- Uses `.place()` for positioning

**Inner Border:**
- Background: #313244 (dark gray)
- Border: 2px ridge
- Padding: 1px (creates shadow gap)

**Title Bar:**
- Background: #45475a (medium gray)
- Height: 32px (fixed)
- Contains title text and control buttons

**Control Buttons:**
- Minimize: Yellow (#f9e2af) with "−"
- Maximize: Blue (#89b4fa) with "□"
- Close: Red (#f38ba8) with "✕"
- Size: 2 characters wide, 1 character height

**Content Frame:**
- Background: #1e1e2e (dark background)
- Fills remaining space
- Where apps are rendered

---

## 📐 Layout System

### Placement Strategy
DoubOS uses **`.place()`** geometry manager for windows:

**Why `.place()`?**
- Absolute positioning (x, y coordinates)
- Allows overlapping windows
- Z-order control with `.lift()`
- Drag-and-drop support

**Desktop Frame uses `.pack()`:**
```python
desktop_frame.pack(fill=tk.BOTH, expand=True)
```

**Windows use `.place()` inside desktop_frame:**
```python
window_frame.place(x=50, y=50, width=800, height=600)
```

**Why NOT Toplevel?**
- Toplevel creates separate OS windows
- We want windows INSIDE the simulation
- Frame-based windows stay contained

---

## 🎯 Window Positioning

### Default Position
New windows start at `(50, 50)` with staggering.

### Staggered Positioning
```python
offset = (window_offset * 30) % 200
x_pos = 50 + offset
y_pos = 50 + offset
```

Example for 5 windows:
1. Window 1: (50, 50)
2. Window 2: (80, 80)
3. Window 3: (110, 110)
4. Window 4: (140, 140)
5. Window 5: (170, 170)

### Bounds
- Offset cycles at 200px to prevent windows going off-screen
- Desktop frame is 1200x800 (minus taskbar)
- Maximum usable area: 1200 x 750

---

## 🖱️ Window Interactions

### Dragging
**Implementation:**
```python
titlebar.bind("<Button-1>", start_drag)  # Mouse down
titlebar.bind("<B1-Motion>", do_drag)    # Mouse drag
```

**Drag Data:**
- Store initial mouse position relative to window
- Calculate new position during drag
- Update window position with `.place()`

**Constraint:**
- Dragging disabled when maximized

### Minimize
**Behavior:**
- Window shrinks to small size (200x30)
- Moves to (0, 0) position
- Button changes from "−" to "▢"
- Click again to restore

**State:**
```python
self.is_minimized = True/False
```

### Maximize
**Behavior:**
- Window fills entire desktop frame
- Uses `relwidth=1, relheight=1`
- Saves original geometry for restore
- Dragging disabled

**State:**
```python
self.is_maximized = True/False
self.original_geometry = (x, y, width, height)
```

### Close
**Behavior:**
- Calls app's `cleanup()` method if it exists
- Destroys window frame
- Removes from windows list

### Focus (Z-Order)
**Implementation:**
```python
window_frame.lift()  # Bring to front
```

---

## 📱 Application Integration

### App Requirements
Apps must be **tk.Frame subclasses** or accept a parent frame.

**Pattern 1: Frame Subclass**
```python
class MyApp(tk.Frame):
    def __init__(self, parent_frame, *args):
        super().__init__(parent_frame, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        # Build UI inside self
```

**Pattern 2: SimulatedApp Base**
```python
class MyApp(SimulatedApp):
    def __init__(self, parent_frame, *args):
        super().__init__(parent_frame)
        
    def setup_ui(self):
        # Build UI inside self.parent_frame
```

### Launching Apps
```python
window_manager.open_window(
    "App Title",      # Window title
    800,              # Width
    600,              # Height
    AppClass,         # App class (not instance)
    arg1, arg2        # Args passed to AppClass.__init__
)
```

### App Lifecycle
1. **WindowManager.open_window()** called
2. **SimulationWindow created** with geometry
3. **Window frame placed** on desktop
4. **App instantiated** inside content_frame
5. **Window lifted** to front
6. **App runs** until window closed
7. **App cleanup()** called if method exists
8. **Window destroyed** and removed from list

---

## 🔍 Debugging Windows

### Print Statements
Window manager includes debug output:
```python
print(f"✓ Window opened at ({x_pos}, {y_pos})")
print(f"Creating app: {app_class.__name__}")
print(f"✓ App created successfully")
```

### Error Handling
If app fails to load:
- Error message displayed in content_frame
- Traceback printed to console
- Window remains open (shows error)

### Verification
Check if window manager is initialized:
```python
if desktop.window_manager:
    print("Window manager ready")
```

---

## ⚡ Performance Considerations

### Window Limit
- No hard limit on number of windows
- Each window consumes memory
- Consider closing unused windows

### Rendering
- Tk handles rendering
- Frame-based windows are lightweight
- Overlapping windows handled efficiently

### Memory
- Each app maintains its own state
- Windows list grows with open windows
- Cleanup happens on close

---

## 🛠️ Advanced Features

### Custom Window Decorations
Modify `SimulationWindow` class:
- Change title bar color
- Add custom buttons
- Modify border style

### Window Events
Add event handlers:
```python
window_frame.bind("<Configure>", on_resize)
window_frame.bind("<FocusIn>", on_focus)
```

### Window State
Save/restore window positions:
```python
state = {
    "windows": [
        {"title": "Terminal", "x": 50, "y": 50, ...}
    ]
}
```

---

## 📋 Best Practices

### 1. App Development
- Always inherit from tk.Frame
- Use `pack(fill=tk.BOTH, expand=True)` for root widget
- Handle cleanup in `cleanup()` method

### 2. Window Management
- Use window_manager.open_window() consistently
- Don't create Toplevel windows directly
- Let window manager handle positioning

### 3. Layout
- Use pack() or grid() inside content_frame
- Don't use place() for app content
- Respect parent_frame boundaries

### 4. Styling
- Match DoubOS color scheme
- Use dark backgrounds (#1e1e2e)
- Use accent colors sparingly

---

## 🎓 Examples

### Simple App
```python
class HelloApp(tk.Frame):
    def __init__(self, parent_frame):
        super().__init__(parent_frame, bg="#1e1e2e")
        self.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(self, text="Hello, DoubOS!",
                        font=("Segoe UI", 20),
                        bg="#1e1e2e", fg="#89b4fa")
        label.pack(expand=True)
```

### Launch It
```python
window_manager.open_window("Hello", 400, 300, HelloApp)
```

### Complex App with Args
```python
class EditorApp(tk.Frame):
    def __init__(self, parent_frame, filename=None):
        super().__init__(parent_frame, bg="#1e1e2e")
        self.filename = filename
        self.pack(fill=tk.BOTH, expand=True)
        # Build editor UI...
```

### Launch with Args
```python
window_manager.open_window(
    "Editor", 800, 600, 
    EditorApp, 
    "document.txt"  # Passed to filename parameter
)
```

---

## 🔗 Related Files

- `window_manager.py` - Window management system
- `windowed_apps.py` - Built-in applications
- `gui_desktop.py` - Desktop environment
- `croptopia_sim.py` - Game example
- `games_menu.py` - Games launcher

---

## 🎉 Summary

DoubOS window system provides:
- ✅ Windows INSIDE desktop simulation (not separate OS windows)
- ✅ Drag, minimize, maximize, close controls
- ✅ Staggered positioning for better UX
- ✅ Z-order management
- ✅ Clean app integration
- ✅ Frame-based architecture
- ✅ Catppuccin-themed styling

**The result:** A true desktop OS experience! 🖥️
