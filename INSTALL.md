# DoubOS Installation Guide

## 🚀 Quick Start

### Option 1: Run Directly (Recommended)

**GUI Mode:**
```bash
python doubos_gui.py
```

**CLI Mode:**
```bash
python doubos.py
```

### Option 2: Create Portable USB Installation

1. Run the installer:
```bash
python create_bootable.py
```

2. Follow the wizard to create a portable installation

3. Copy the `DoubOS` folder to your USB drive

4. Run from anywhere!

## 📋 System Requirements

- **Python:** 3.7 or higher
- **Libraries:** Tkinter (included with Python)
- **Storage:** ~50MB
- **OS:** Windows, Linux, or macOS

## 🎯 Features

### Desktop Environment
- ✅ Full graphical interface with taskbar
- ✅ Start menu with app launcher
- ✅ Desktop icons and shortcuts
- ✅ Window management
- ✅ System tray

### Applications
- 📁 File Explorer (browse virtual filesystem)
- 💻 Terminal (50+ commands)
- 📝 Text Editor (create/edit files)
- 🔢 Calculator (scientific mode)
- ⚙️ Settings (system configuration)
- 👤 User Manager (create/manage users)
- 🎮 Games (Snake, Pong, Memory)
- 📊 System Monitor (CPU, RAM, uptime)
- 🌐 Web Browser (basic)
- 🎨 Theme Customizer
- 📦 Package Manager
- 🔍 Search Tool
- 📷 Screenshot Tool

### Commands (50+)
Navigation: `cd`, `ls`, `pwd`, `tree`
Files: `cat`, `touch`, `mkdir`, `rm`, `cp`, `mv`, `nano`
System: `whoami`, `uptime`, `ps`, `kill`, `clear`, `history`
Network: `ping`, `wget`, `curl`, `ifconfig`
Dangerous: `format`, `nuke`, `shred`, `wipe` (SAFE - virtual only!)
Fun: `cowsay`, `fortune`, `matrix`, `hacker`, `joke`
And many more...

## 👤 Default Users

1. **admin** / admin123 (Administrator)
2. **user** / password (Standard user)
3. **guest** / guest (Guest access)

Or create your own account at login!

## 🔧 Usage Examples

### Creating a Portable Installation

```bash
# Run the installer
python create_bootable.py

# Select option 1 or 2
# Follow prompts

# Result: DoubOS folder ready to copy to USB!
```

### Running from USB

**Windows:**
```
DoubOS\boot\start_doubos.bat
```

**Linux/Mac:**
```bash
bash DoubOS/boot/start_doubos.sh
```

### Command Examples

```bash
# Create directory structure
mkdir projects
cd projects
mkdir myapp
cd myapp

# Create files
touch README.md
nano app.py

# List files
ls -la

# Search
find . -name "*.py"
grep "import" app.py

# Network
ping google.com
wget example.com

# Fun stuff
cowsay "Hello DoubOS!"
matrix
hacker
```

## 🎨 Customization

### Change Theme
1. Open Settings app
2. Go to Appearance
3. Select color scheme
4. Apply changes

### Create Custom Commands
Edit `commands.py` and add your own commands!

### Modify Desktop Icons
Edit `gui_desktop.py` to customize desktop shortcuts

## ⚡ Performance Tips

1. **Virtual Filesystem:** Saves to disk automatically
2. **Lazy Loading:** Apps load only when opened
3. **Memory Efficient:** ~50MB RAM usage
4. **Fast Startup:** <2 seconds boot time

## 🛡️ Safety Features

### All Dangerous Commands are VIRTUAL!
- `format` - Wipes virtual filesystem (your real files are safe!)
- `nuke` - Total virtual destruction
- `shred` - Secure virtual file deletion
- `wipe` - Clean virtual data

**Your real computer is 100% safe!**

## 📚 Documentation

- **README.md** - Complete documentation
- **QUICKSTART.md** - Quick start guide
- **FEATURES.md** - Feature showcase
- **COMMANDS.md** - Command reference
- **INSTALL.md** - This file

## 🐛 Troubleshooting

### "No module named 'tkinter'"
**Windows:**
```
Reinstall Python with "tcl/tk and IDLE" checked
```

**Linux:**
```bash
sudo apt install python3-tk
```

**Mac:**
```bash
brew install python-tk
```

### "Permission denied"
Run with appropriate permissions:
```bash
python3 doubos_gui.py
```

### GUI doesn't start
Make sure you have Python 3.7+:
```bash
python --version
```

## 🔄 Updates

DoubOS saves your data automatically:
- **doubos_filesystem.json** - Virtual filesystem
- **doubos_users.json** - User accounts

Keep these files to preserve your data between sessions!

## 🌟 Advanced Features

### Multi-User Support
- Create unlimited users
- Administrator privileges
- Password protection
- Session management

### Persistent Storage
- Auto-save on exit
- JSON-based storage
- Easy backup/restore

### Extensible Architecture
- Plugin-style command system
- Modular GUI apps
- Easy to add new features

## 📖 Learning Resources

DoubOS is perfect for learning:
- **Operating System Concepts**
- **File Systems**
- **User Management**
- **GUI Programming**
- **Python Development**

## 🎓 Educational Use

Great for:
- CS students learning OS concepts
- Python programming practice
- Understanding filesystems
- GUI development
- System administration basics

## 🤝 Contributing

Want to add features? Edit the source:
- `commands.py` - Add commands
- `gui_apps.py` - Add GUI applications
- `filesystem.py` - Modify file system
- `gui_desktop.py` - Customize desktop

## 📝 License

DoubOS is for educational purposes.
Enjoy and learn! 🚀

---

**Made with ❤️ for learning and experimentation**

Version 1.0.0
