# DoubOS - A Fully Fledged Operating System Simulator

![DoubOS](https://img.shields.io/badge/DoubOS-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Overview

**DoubOS** is a comprehensive, fully-fledged operating system simulator built in Python! It features a complete virtual file system, user management, process simulation, and over 50+ commands including some VERY dangerous ones! 💀

## ⚡ Features

### Core OS Components
- **Virtual File System** - Complete Unix-like directory structure with files and directories
- **User Management** - Multi-user support with authentication and permissions
- **Command-Line Shell** - Interactive shell with command history and aliases
- **Process Simulation** - Simulated process management
- **Environment Variables** - Customizable system environment

### 📁 File System
- Create, read, update, and delete files
- Directory navigation (cd, pwd, ls)
- File operations (cp, mv, rm, mkdir, touch, cat)
- Persistent storage (save/load sessions)
- Permission system

### 👥 User System
- Multiple user accounts (root, admin, guest)
- Password authentication
- Admin privileges
- User home directories
- Session management

### 💻 Commands (50+!)

#### Navigation
- `cd`, `pwd`, `ls`, `ll`, `la`

#### File Operations
- `cat`, `touch`, `mkdir`, `rm`, `cp`, `mv`
- `echo`, `grep`, `find`, `head`, `tail`, `wc`

#### System Info
- `date`, `uptime`, `whoami`, `uname`, `history`
- `df`, `ps`, `top`, `env`, `users`

#### Network Simulation
- `ping`, `wget`, `curl`, `ifconfig`

#### Package Manager
- `apt install/update/upgrade/remove`

#### Dangerous Commands ⚠️
- `format` - Wipe entire file system
- `nuke` - Complete system annihilation (filesystem + users)
- `shred` - Securely delete files
- `wipe` - Destroy directories
- `corrupt` - Corrupt file data
- `forkbomb` - Process explosion simulation
- `logbomb` - Fill logs with data
- `killall` - Terminate all processes

#### Fun Commands 🎉
- `cowsay` - ASCII cow
- `fortune` - Random fortunes
- `joke` - Programming jokes
- `hacker` - Enter 1337 mode
- `matrix` - Enter the Matrix
- `ascii` - DoubOS art
- `weather` - Weather simulation
- `dice`, `flip` - Random generators
- `colors` - Color palette

#### Utilities
- `tar` - Archive files
- `chmod`, `chown` - Permissions
- `help`, `man` - Documentation
- `clear`, `alias`

### 🎨 User-Friendly Features
- Colorized output
- Command aliases
- Interactive prompts
- Helpful error messages
- Extensive help system
- Session persistence

## 📦 Installation

No installation required! Just Python 3.7+

```bash
# Clone or download the DoubOS files
cd DoubOS

# Run DoubOS
python doubos.py
```

## 🎮 Usage

### Starting DoubOS

```bash
python doubos.py
```

### Login Credentials

Default users:
- **root** - password: `root123` (admin)
- **admin** - password: `admin123` (admin)
- **guest** - password: `guest` (regular user)

### Example Session

```bash
# Login as admin
Username: admin
Password: admin123

# Navigate and explore
admin@DoubOS:/home/admin$ ls /
bin  dev  etc  home  proc  sbin  tmp  usr  var

admin@DoubOS:/home/admin$ cat /etc/motd
Welcome to DoubOS!
A powerful operating system simulator.

# Create files
admin@DoubOS:/home/admin$ echo "Hello DoubOS!" > test.txt
admin@DoubOS:/home/admin$ cat test.txt
Hello DoubOS!

# Try some fun commands
admin@DoubOS:/home/admin$ fortune
You will write bug-free code today... or will you?

admin@DoubOS:/home/admin$ cowsay "DoubOS is awesome!"
 ___________________
< DoubOS is awesome! >
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

# Get help
admin@DoubOS:/home/admin$ help
[Lists all available commands]

# Exit
admin@DoubOS:/home/admin$ exit
```

### ⚠️ Dangerous Commands Demo

```bash
# Format the file system (requires admin)
admin@DoubOS:/$ format --confirm
🔥 FORMATTING FILE SYSTEM 🔥
⚠️  All data has been erased!

# Nuclear option (EVERYTHING)
admin@DoubOS:/$ nuke --i-am-absolutely-sure
☢️  NUKING ALL SYSTEMS
💀 SYSTEM ANNIHILATED 💀
```

## 🗂️ Project Structure

```
DoubOS/
├── doubos.py              # Main entry point
├── kernel.py              # OS kernel and shell
├── filesystem.py          # Virtual file system
├── users.py              # User management
├── commands.py           # Built-in commands
├── dangerous_commands.py # Dangerous system commands
├── utilities.py          # Utility commands
├── fun_commands.py       # Fun/Easter egg commands
└── README.md             # This file
```

## 🔧 Technical Details

### Architecture
- **Kernel**: Manages system state, uptime, environment
- **Shell**: Interactive command-line interface
- **File System**: Tree-based virtual filesystem with persistence
- **User Manager**: Authentication and session management
- **Command Processor**: Parses and executes commands

### File System
- Unix-like directory structure
- File metadata (owner, permissions, timestamps)
- Recursive operations
- JSON serialization for persistence

### Security
- Password hashing (SHA-256)
- User/admin privilege separation
- Permission checks for dangerous commands

## 🎯 Use Cases

- **Learning**: Understand OS concepts (filesystem, users, processes)
- **Experimentation**: Safe environment to try destructive commands
- **Fun**: Enjoy the Easter eggs and fun commands
- **Development**: Extend with your own commands
- **Education**: Teach OS fundamentals without real risks

## 🚨 Safety Notice

DoubOS is a **SIMULATION**. All destructive commands are safe:
- ✅ No actual files are harmed
- ✅ Your real system is safe
- ✅ All operations are virtual
- ✅ Easy reset with `nuke` command

## 🛠️ Extending DoubOS

Add your own commands by creating a new Command class:

```python
from commands import Command, CommandContext
from typing import List

class MyCommand(Command):
    def __init__(self):
        super().__init__(
            "mycommand",
            "Description of my command",
            "mycommand <args>"
        )
    
    def execute(self, args: List[str], context: CommandContext) -> str:
        return "Hello from my command!"

# Register in doubos.py
processor.register_command(MyCommand())
```

## 📝 Command Cheat Sheet

| Category | Commands |
|----------|----------|
| **Navigation** | cd, pwd, ls, ll, la |
| **Files** | cat, touch, mkdir, rm, cp, mv, echo |
| **Search** | grep, find |
| **System** | date, uptime, whoami, uname, history, env |
| **Users** | users, passwd, su |
| **Network** | ping, wget, curl, ifconfig |
| **Info** | df, ps, top |
| **Package** | apt |
| **Archive** | tar |
| **Permissions** | chmod, chown |
| **Text** | head, tail, wc |
| **Power** | shutdown, exit, reboot |
| **DANGER** | format, nuke, shred, wipe, corrupt |
| **Fun** | cowsay, fortune, joke, hacker, matrix, weather |

## 🎓 Learning Resources

DoubOS teaches:
- File system concepts
- User authentication
- Command-line interfaces
- Operating system design
- Shell scripting basics

## 🤝 Contributing

Feel free to extend DoubOS with:
- New commands
- Additional features
- UI improvements
- Bug fixes
- Documentation

## 📜 License

MIT License - Feel free to use, modify, and distribute!

## 👨‍💻 Author

Created as a fully-fledged OS playground for learning and experimentation.

## 🎉 Have Fun!

Remember: In DoubOS, you can safely do things that would be catastrophic in a real OS!

```
admin@DoubOS:/$ nuke --i-am-absolutely-sure
💀 SYSTEM ANNIHILATED 💀
```

**Enjoy your virtual operating system!** 🚀

---

*DoubOS - Where you can safely destroy everything and start over!* 💾
