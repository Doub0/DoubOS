# DoubOS GUI - User Guide

## 🎉 Welcome to DoubOS!

DoubOS is a fully-featured desktop operating system simulator with a beautiful graphical interface.

---

## 🚀 Getting Started

### Method 1: Using the Launcher (Recommended)
```bash
python launcher.py
```

This will show a menu with options:
- **Login with credentials** - Full login screen experience
- **Quick test (auto-login)** - Skip login for testing
- **Run comprehensive test** - Verify system integrity
- **Exit** - Close launcher

### Method 2: Direct Launch
```bash
# Full system with login screen
python doubos_gui.py

# Auto-login test mode
python doubos_test.py

# Comprehensive system test
python test_comprehensive.py
```

---

## 🔐 Login Credentials

**Default Administrator Account:**
- Username: `admin`
- Password: `admin123`

You can also create new accounts using the "Create Account" button on the login screen.

---

## 🖥️ Desktop Features

### Desktop Icons
The desktop has **6 quick-launch icons**:
1. **💻 Terminal** - Command-line interface with 15+ commands
2. **📁 Files** - File browser (virtual filesystem)
3. **⚙️ Settings** - Theme and system settings
4. **📝 Text Editor** - Multi-file text editor
5. **🧮 Calculator** - Basic calculations
6. **🎮 Games** - Games menu with Croptopia

### START Menu
Click the **⊞ START** button to access:
- All 10 applications
- Power options (Lock, Restart, Shutdown)
- User information

### Taskbar Quick Launch
Click the icons on the taskbar:
- 🌐 Browser (coming soon)
- 📧 Mail (coming soon)
- 🎵 Music (coming soon)
- 🖼️ Photos (coming soon)

### System Tray
The right side of the taskbar shows:
- Current time and date
- Logged-in user
- System icons (Volume, Network, Battery)

---

## 📦 Applications

### 1. Terminal 💻
**Full-featured command-line interface**

Commands available:
- **File management:** `ls`, `cd`, `pwd`, `mkdir`, `touch`, `cat`, `rm`
- **System info:** `whoami`, `uptime`, `date`, `clear`
- **Fun commands:** `cowsay`, `fortune`, `hacker`, `matrix`, `joke`
- **Help:** Type `help` to see all commands

Features:
- Command history (↑/↓ arrows)
- Color-coded output
- Scrollable output area

### 2. File Explorer 📁
Browse your virtual filesystem with a tree view interface.

Default folders:
- Documents
- Downloads
- Pictures
- Projects

### 3. Text Editor 📝
Simple text editor with toolbar:
- New file
- Open file
- Save file

### 4. Calculator 🧮
Basic calculator with:
- Number pad
- Basic operations (+, -, ×, ÷)
- Decimal support

### 5. Settings ⚙️
View and manage system settings:
- Theme selection
- System configuration
- User preferences

### 6. Games Menu 🎮
Access to available games:
- **Croptopia** - Farming simulation game

---

## 🌾 Croptopia - Game Guide

**Farming simulation game** - Plant, water, and harvest crops!

### How to Play:
1. **Start Money:** $100
2. **Plant Crops:** Click empty cells and select a crop
   - 🍎 Apple - $10 to plant
   - 🥕 Carrot - $10 to plant
   - 🌾 Wheat - $10 to plant

3. **Water Crops:** Click "💧 Water All" button

4. **Wait for Growth:** Click "🌙 Next Day" to advance time
   - Crops take 3 days to grow

5. **Harvest:** Click mature crops to harvest and earn money
   - Harvest rewards vary by crop

6. **Inventory:** Track your harvested crops

### Tips:
- Plant multiple crops for better profits
- Water regularly for best growth
- Harvest mature crops quickly to replant

---

## 🎨 Window Management

### Window Controls
Every application window has:
- **Title Bar** - Shows app name, drag to move window
- **− Minimize** (Yellow) - Minimize to taskbar
- **□ Maximize** (Blue) - Maximize to full screen
- **✕ Close** (Red) - Close the window

### Window Features:
- **Drag windows** - Click and drag the title bar
- **Multiple windows** - Open several apps at once
- **Z-order** - Click any window to bring it to front
- **Offset positioning** - New windows automatically stagger

---

## ⌨️ Keyboard Shortcuts

### Terminal
- **↑ / ↓** - Navigate command history
- **Enter** - Execute command

### General
- **Alt+F4** - Quit DoubOS (Windows)
- **Cmd+Q** - Quit DoubOS (macOS)

---

## 🔒 Power Options

Access via START menu:

### Lock 🔒
Locks the desktop and returns to login screen.

### Restart 🔄
Restarts the desktop environment (keeps session).

### Shutdown ⏻
Saves state and closes DoubOS completely.

---

## 🎨 Themes

DoubOS currently uses the **Catppuccin Mocha** theme:
- Dark background (#1e1e2e)
- Blue accents (#89b4fa)
- Soft text colors (#cdd6f4)

More themes coming soon!

---

## 💾 Data Persistence

DoubOS automatically saves:
- **Filesystem** - Files and folders (doubos_filesystem.json)
- **Users** - Account data (doubos_users.json)

These are saved automatically on shutdown.

---

## 🐛 Troubleshooting

### Windows not appearing?
- Make sure you're clicking desktop icons or START menu items
- Check if windows are appearing behind other windows
- Try closing all windows and opening a new one

### Apps not launching?
- Check the terminal output for error messages
- Verify all dependencies are installed: `pip install tkinter`
- Run the comprehensive test: `python test_comprehensive.py`

### Login issues?
- Default credentials: admin / admin123
- Click "Create Account" to make a new account
- Users are saved in doubos_users.json

### Game not loading?
- Make sure you clicked the Games icon/menu item
- Click "▶ Play Game" button in the Games menu
- Croptopia should open in a new window

---

## 📊 System Requirements

- **Python:** 3.7 or higher
- **Tkinter:** Built-in with Python (usually)
- **Platform:** Windows, macOS, Linux
- **Display:** Minimum 1200x800 resolution recommended

---

## 🛠️ Advanced Features

### Virtual Filesystem
- JSON-based storage
- Persistent across sessions
- Full CRUD operations

### User Management
- SHA-256 password hashing
- Admin and standard user types
- Multi-user support

### Window Manager
- Frame-based windows (inside simulation)
- No separate OS windows
- Z-order management
- Minimize/maximize/close controls

---

## 📝 Tips & Tricks

1. **Multiple Windows:** Open several apps to test multitasking
2. **Terminal Fun:** Try `cowsay hello` or `matrix` for fun
3. **Games:** Launch Croptopia from Games menu for farming
4. **Window Dragging:** Drag windows by their title bars
5. **Quick Launch:** Use desktop icons for faster access

---

## 🌟 What's Next?

Upcoming features:
- More games
- Web browser simulation
- Music player
- Photo viewer
- Email client
- System monitor with live stats
- More themes
- File operations in File Explorer
- Save/load in Text Editor

---

## 📚 Additional Resources

- **README.md** - Installation and setup
- **COMMANDS.md** - Full command reference
- **FEATURES.md** - Complete feature list
- **QUICKSTART.md** - 5-minute guide

---

## 🤝 Support

For issues or questions:
1. Run comprehensive test to verify system
2. Check error messages in terminal
3. Review this guide for usage tips

---

## 🎉 Enjoy DoubOS!

You now have a fully functional desktop OS simulator. Explore, experiment, and have fun!

**Happy computing! 🚀**
