# 🚀 DoubOS - Fully-Featured Desktop Operating System

```
██████╗  ██████╗ ██╗   ██╗██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║██║   ██║██████╔╝██║   ██║███████╗
██║  ██║██║   ██║██║   ██║██╔══██╗██║   ██║╚════██║
██████╔╝╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝███████║
╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

        Complete Desktop OS with GUI & 50+ Commands
              Safe • Educational • User-Friendly
```

## ⚡ Quick Start

### Windows
```batch
start_doubos.bat
```

### Linux/Mac
```bash
bash start_doubos.sh
```

### Or Directly
```bash
python doubos_gui.py  # GUI Desktop
python doubos.py      # Terminal Only
```

## 🎯 What is DoubOS?

DoubOS is a **complete operating system simulator** with:

✅ **Full GUI Desktop Environment** - Taskbar, start menu, windowing system  
✅ **50+ Terminal Commands** - Like real Linux/Unix systems  
✅ **13 GUI Applications** - File explorer, text editor, games, and more  
✅ **Virtual Filesystem** - Complete file system that persists between sessions  
✅ **Multi-User Support** - Create accounts, login, manage permissions  
✅ **8 Beautiful Themes** - Catppuccin, Dracula, Nord, Tokyo Night, and more  
✅ **Dangerous Commands** - format, nuke, shred (100% SAFE - virtual only!)  
✅ **USB Bootable** - Create portable installation on USB drive  
✅ **Zero Dependencies** - Uses only Python standard library + Tkinter  
✅ **Cross-Platform** - Works on Windows, Linux, and macOS  

**Everything is 100% safe and virtual - your real files are never touched!**

## 🖥️ Desktop Environment

### Taskbar & Start Menu
- Beautiful modern design with 8 color themes
- Application launcher with search
- Quick launch icons
- System tray with clock
- Window management (minimize/maximize/close)

### Desktop Icons
- Files (File Explorer)
- Terminal
- Documents (Text Editor)
- Games
- Settings
- User Manager

## 📱 Built-in Applications (13 Total)

### 1. **Terminal** 💻
- 50+ commands (ls, cd, cat, grep, ping, wget, etc.)
- Command history (↑/↓ keys)
- Auto-completion
- ANSI colors
- Dangerous commands (format, nuke, shred - all safe!)

### 2. **File Explorer** 📁
- Tree view navigation
- Create/delete files & folders
- Copy/move operations
- File preview
- Properties panel

### 3. **Text Editor** 📝
- Create and edit documents
- Syntax highlighting
- Line numbers
- Find & replace
- Auto-save

### 4. **Calculator** 🔢
- Basic operations
- Scientific mode
- Memory functions
- Keyboard support

### 5. **Settings** ⚙️
- Theme customization (8 themes!)
- System configuration
- Display settings
- User preferences

### 6. **User Manager** 👥
- Create new users
- Manage passwords
- Set permissions (admin/standard)
- View user activity

### 7. **Games** 🎮
- **Snake** - Classic arcade
- **Pong** - Two-player
- **Memory** - Card matching
- High scores & difficulty levels

### 8. **System Monitor** 📊
- CPU usage
- Memory statistics
- Process list
- Real-time updates

### 9. **Web Browser** 🌐
- Basic HTML rendering
- Bookmarks
- History
- (Educational purposes)

### 10. **Theme Customizer** 🎨
- Live theme preview
- 8 pre-made themes
- Create custom themes
- Export/import

### 11. **Package Manager** 📦
- Install packages (simulated)
- Update software
- Dependency resolution

### 12. **Search Tool** 🔍
- File search
- Content search (grep)
- Regular expressions

### 13. **Screenshot Tool** 📷
- Capture desktop
- Save screenshots
- Region selection

## 💻 Command Line (50+ Commands)

### Navigation
```bash
ls          # List files
cd path     # Change directory
pwd         # Print working directory
tree        # Directory tree view
find name   # Search for files
```

### File Operations
```bash
cat file      # Display content
touch file    # Create file
mkdir dir     # Create directory
rm file       # Remove file/dir
cp src dst    # Copy
mv old new    # Move/rename
nano file     # Edit file
```

### System Commands
```bash
whoami      # Current user
uptime      # System uptime
ps          # List processes
kill pid    # Terminate process
clear       # Clear screen
history     # Command history
date        # Show date/time
```

### Network (Simulated)
```bash
ping host     # Test connectivity
wget url      # Download file
curl url      # Transfer data
ifconfig      # Network config
```

### Dangerous Commands ⚠️
**ALL SAFE - Virtual filesystem only!**
```bash
format      # Wipe entire filesystem
nuke        # Total destruction
shred file  # Secure deletion
wipe dir    # Clean thoroughly
```

### Fun Commands
```bash
cowsay msg    # ASCII cow
fortune       # Random quotes
matrix        # Matrix effect
hacker        # Hacker simulator
joke          # Random jokes
```

## 🎨 Themes

Choose from 8 beautiful color schemes:

1. **Catppuccin Mocha** (Default) - Smooth purple/blue
2. **Dracula** - Classic dark with purple
3. **Gruvbox Dark** - Warm retro colors
4. **Nord** - Cool arctic palette
5. **Tokyo Night** - Japanese-inspired
6. **Solarized Dark** - Eye-friendly
7. **Monokai** - Classic editor theme
8. **One Dark** - Atom-inspired

Change themes in **Settings → Appearance**

## 👤 User System

### Default Users
- **admin** / admin123 (Administrator)
- **user** / password (Standard user)
- **guest** / guest (Guest access)

### Create New Users
1. Click "Create Account" at login screen
2. Or use **User Manager** app
3. Set username, password, and permissions

### Features
- Password authentication (SHA-256)
- User roles (admin/standard/guest)
- Session management
- Activity logging

## 💾 Virtual Filesystem

### Persistent Storage
- Saves automatically on exit
- Restores on next launch
- JSON-based (human-readable)
- Safe from real filesystem

### Default Structure
```
/
├── home/
│   ├── admin/
│   ├── user/
│   └── guest/
├── system/
│   ├── bin/
│   ├── lib/
│   └── etc/
├── tmp/
└── var/
```

## 📦 USB Installation

### Create Portable Installation
```bash
python create_bootable.py
```

Follow the wizard to create a portable DoubOS that can:
- Run from USB drive
- No installation required
- Works on any computer
- Copy between systems

The installer creates:
- Complete DoubOS system
- Launcher scripts (Windows & Linux)
- Documentation
- Auto-run configuration

## 🚀 Performance

### Optimized for Speed
- **Fast startup**: <2 seconds
- **Low RAM**: ~50MB usage
- **Small size**: ~500KB total
- **Efficient I/O**: Lazy loading & caching

### Performance Monitoring
- CPU usage tracking
- Memory profiling
- Command timing
- Cache hit rates
- Performance reports

## 📚 Documentation

- **README.md** (this file) - Complete overview
- **QUICKSTART.md** - 5-minute tutorial
- **FEATURES.md** - Comprehensive feature list
- **COMMANDS.md** - All command reference
- **INSTALL.md** - Installation guide

## 🎓 Educational Value

Perfect for learning:
- **Operating System Concepts**
- **File Systems**
- **User Management**
- **Process Scheduling**
- **GUI Programming** (Tkinter)
- **Python OOP**
- **System Architecture**

Great for:
- Computer Science students
- Programming practice
- OS course projects
- Interview preparation
- Teaching tool

## 🔧 Technical Details

### Requirements
- **Python**: 3.7 or higher
- **Libraries**: Tkinter (included with Python)
- **Storage**: ~50MB
- **RAM**: ~50MB
- **OS**: Windows, Linux, or macOS

### Architecture
- **Language**: Python
- **GUI Framework**: Tkinter
- **Storage**: JSON files
- **Security**: SHA-256 password hashing
- **Design**: Object-oriented, command pattern

### File Structure
```
DoubOS/
├── doubos.py               # CLI launcher
├── doubos_gui.py           # GUI launcher
├── kernel.py               # OS kernel
├── filesystem.py           # Virtual FS
├── users.py                # User management
├── commands.py             # Built-in commands
├── dangerous_commands.py   # Destructive operations
├── utilities.py            # Advanced tools
├── fun_commands.py         # Easter eggs
├── gui_desktop.py          # Desktop environment
├── gui_apps.py             # GUI applications
├── gui_login.py            # Login screen
├── theme_manager.py        # Theme system
├── performance_monitor.py  # Performance tracking
├── create_bootable.py      # USB installer
├── start_doubos.bat        # Windows launcher
├── start_doubos.sh         # Linux/Mac launcher
└── docs/                   # Documentation
```

## 🛡️ Safety Features

### 100% Safe & Virtual
- **No real files touched** - Everything is virtual
- **Sandboxed environment** - Isolated from real system
- **Reversible operations** - Reset anytime
- **Safe dangerous commands** - format, nuke, shred are virtual only

You can safely:
- Try destructive commands
- Experiment with file systems
- Learn without risk
- Make mistakes

## 🎮 Fun Features

### Easter Eggs
Try these commands:
- `cowsay "Hello!"`
- `matrix`
- `hacker`
- `fortune`
- `joke`

### Games
- **Snake**: Classic arcade action
- **Pong**: Two-player competition
- **Memory**: Brain training

### Hidden Features
Explore and discover more!

## 📈 Statistics

- **Lines of Code**: 5,000+
- **Commands**: 50+
- **Applications**: 13
- **Themes**: 8
- **File Size**: ~500KB
- **RAM Usage**: ~50MB
- **Startup Time**: <2 seconds

## 🤝 Contributing

DoubOS is designed to be extended!

### Add Your Own Commands
Edit `commands.py` and create new command classes.

### Create Custom Themes
Use the Theme Customizer app or edit `theme_manager.py`.

### Build New Apps
Add to `gui_apps.py` following the existing patterns.

### Extend the System
Modular architecture makes it easy to add features!

## 🐛 Troubleshooting

### Tkinter Not Found
**Windows**: Reinstall Python, check "tcl/tk and IDLE"  
**Linux**: `sudo apt install python3-tk`  
**Mac**: `brew install python-tk`

### Python Version Too Old
Update to Python 3.7+:  
Download from [python.org](https://www.python.org/downloads/)

### GUI Won't Start
1. Check Python version: `python --version`
2. Verify Tkinter: `python -c "import tkinter"`
3. Try CLI mode: `python doubos.py`

### Lost Password
Delete `doubos_users.json` to reset to default users.

## 📖 Examples

### Create a Project
```bash
# Open Terminal
mkdir my_project
cd my_project
touch README.md
nano README.md
# Write content
# Save (Ctrl+X)
ls -la
```

### Try Dangerous Commands
```bash
# List everything
ls

# WIPE IT ALL (safely!)
format

# Check - it's gone!
ls

# Exit and restart - it's back!
```

### Customize Theme
1. Open **Settings**
2. Click **Appearance**
3. Select **Tokyo Night**
4. Click **Apply**
5. Enjoy new colors!

## 🌟 Why DoubOS?

### Educational
- Learn real OS concepts
- Safe environment to experiment
- Understand filesystems
- Practice commands

### Fun
- Play games
- Customize desktop
- Try dangerous commands safely
- Discover easter eggs

### Practical
- Portable (USB drive)
- No installation needed
- Cross-platform
- Zero dependencies

### Complete
- Full desktop environment
- 50+ commands
- 13 applications
- 8 themes
- Comprehensive docs

## 🔮 Future Ideas

Potential additions:
- Networking simulation
- Multi-user chat
- Plugin system
- More games
- Sound support
- Advanced graphics
- Virtual hardware

## 📝 License

Educational and experimental use.  
Made with ❤️ for learning!

## 🎉 Credits

DoubOS - A complete, safe, and educational operating system experience!

Built entirely in Python with:
- Tkinter for GUI
- JSON for storage
- Standard library only
- No external dependencies!

---

## Get Started Now!

```bash
# Windows
start_doubos.bat

# Linux/Mac
bash start_doubos.sh

# Or directly
python doubos_gui.py
```

**Welcome to DoubOS - Where learning meets experimentation!** 🚀

Version 1.0.0 | Python 3.7+ | Cross-Platform | Zero Dependencies
