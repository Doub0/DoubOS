# DoubOS Features Showcase

## 🎯 What Makes DoubOS Special?

DoubOS is a **fully-fledged operating system simulator** that gives you the power to:
- Safely experiment with dangerous commands
- Learn OS concepts hands-on
- Have fun with creative commands
- Build your own extensions

---

## 🌟 Highlighted Features

### 1. Complete File System
```bash
# Unix-like directory structure
/
├── bin/          # System binaries
├── etc/          # Configuration files
├── home/         # User directories
│   ├── admin/
│   └── guest/
├── tmp/          # Temporary files
├── usr/          # User programs
└── var/          # Variable data
    └── log/      # System logs

# Full file operations
mkdir mydir
cd mydir
echo "Hello" > file.txt
cat file.txt
cp file.txt backup.txt
rm file.txt
```

### 2. Multi-User System
```bash
# Three default users
root   - Full administrator (password: root123)
admin  - Administrator     (password: admin123)
guest  - Regular user      (password: guest)

# User management
users              # List all users
whoami             # Current user
# passwd           # Change password (planned)
```

### 3. Dangerous Commands (SAFE!)

#### 💀 Format - Wipe Everything
```bash
admin@DoubOS:/$ format --confirm

🔥 FORMATTING FILE SYSTEM 🔥
⏳ Erasing all data...
   [Clearing superblock...] ✓
   [Zeroing inode tables...] ✓
   [Wiping data blocks...] ✓
✅ File system formatted successfully!
```

#### ☢️ Nuke - Total Annihilation
```bash
admin@DoubOS:/$ nuke --i-am-absolutely-sure

☢️☢️☢️ NUCLEAR OPTION ☢️☢️☢️
⏰ Countdown: 5... 4... 3... 2... 1... 💥
🔥 NUKING ALL SYSTEMS:
   [Wiping file system...] ☢️
   [Removing users...] ☢️
   [Clearing history...] ☢️
💀 SYSTEM ANNIHILATED 💀
```

#### 🔒 Shred - Secure Deletion
```bash
admin@DoubOS:/tmp$ shred sensitive.txt

🔒 Securely shredding: sensitive.txt
   Pass 1/7: Overwriting with random data... ✓
   Pass 2/7: Overwriting with random data... ✓
   ...
✓ File securely erased!
```

#### 🗑️ Wipe - Directory Destruction
```bash
admin@DoubOS:/$ wipe /tmp/olddata --confirm

✓ Wiped /tmp/olddata (47 items deleted)
```

### 4. Network Simulation

#### Ping
```bash
admin@DoubOS:/$ ping google.com

PING google.com (192.168.1.42): 56 data bytes
64 bytes from google.com: icmp_seq=0 ttl=64 time=12.3 ms
64 bytes from google.com: icmp_seq=1 ttl=64 time=11.8 ms
--- google.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss
```

#### Download Files
```bash
admin@DoubOS:/tmp$ wget http://example.com/file.zip

--2026-01-30 10:30:00-- http://example.com/file.zip
Resolving host... 234 ms
Connecting to host... connected.
HTTP request sent, awaiting response... 200 OK
Length: 524288 (512.0K)
Saving to: 'file.zip'
100%[========================================>] 524,288 bytes
'file.zip' saved
```

### 5. Package Manager
```bash
admin@DoubOS:/$ apt update
Reading package lists... Done
All packages are up to date.

admin@DoubOS:/$ apt install nginx
Reading package lists... Done
The following NEW packages will be installed:
  nginx
Setting up nginx ...
✓ nginx installed successfully!
```

### 6. Fun & Easter Eggs

#### 🐮 Cowsay
```bash
admin@DoubOS:/$ cowsay "DoubOS is amazing!"

 ____________________
< DoubOS is amazing! >
 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

#### 🔮 Fortune
```bash
admin@DoubOS:/$ fortune
To err is human, to really screw up requires root access.
```

#### 👨‍💻 Hacker Mode
```bash
admin@DoubOS:/$ hacker

██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║██║     █████╔╝ █████╗  ██████╔╝

[INITIALIZING HACK MODE...]
[Bypassing firewall...] ✓
🎉 You are now 1337! 🎉
```

#### 😄 Jokes
```bash
admin@DoubOS:/$ joke
Why do programmers prefer dark mode?
Because light attracts bugs! 🐛
```

### 7. System Information

#### System Status
```bash
admin@DoubOS:/$ uptime
System uptime: 0h 15m 42s

admin@DoubOS:/$ uname -a
DoubOS 1.0.0 (Virtual OS Simulator)

admin@DoubOS:/$ top
DoubOS System Monitor
Uptime: 0h 15m 42s
User: admin
Processes: 2 total
Memory: Virtual (unlimited)
```

#### File System
```bash
admin@DoubOS:/$ df
Filesystem     Size    Used
/             Virtual  45231B

admin@DoubOS:/$ ls -l /home
drwxr-xr-x admin     0 Jan 30 10:15 admin/
drwxr-xr-x guest     0 Jan 30 10:15 guest/
```

### 8. Advanced Utilities

#### Search
```bash
# Find files
admin@DoubOS:/$ find /home -name "*.txt"
/home/admin/notes.txt
/home/admin/todo.txt

# Search within files
admin@DoubOS:/$ grep "important" /home/admin/notes.txt
This is important information
Another important note
```

#### File Analysis
```bash
# Word count
admin@DoubOS:/$ wc document.txt
      45     321    2456 document.txt

# First/Last lines
admin@DoubOS:/$ head -n 5 log.txt
admin@DoubOS:/$ tail -n 10 log.txt
```

#### Archives
```bash
admin@DoubOS:/$ tar -czf backup.tar.gz file1.txt file2.txt
tar: Creating archive 'backup.tar.gz'
tar: backup.tar.gz created successfully (12847 bytes)
```

### 9. Colorized Output
DoubOS uses colors for better readability:
- 🔵 **Blue** - Directories
- 🟢 **Green** - User prompts
- 🔴 **Red** - Errors and warnings
- ⚪ **White** - Regular files

### 10. Session Persistence
```bash
# Save your work
admin@DoubOS:/$ exit
Save session for next time? (y/n): y
✓ System state saved

# Later...
$ python doubos.py
Load previous session? (y/n): y
✓ Filesystem loaded from disk
✓ Users loaded from disk
```

---

## 🎮 Example Workflows

### Workflow 1: File Management
```bash
# Create project structure
mkdir /home/admin/project
cd /home/admin/project
mkdir src docs tests

# Create files
echo "# My Project" > README.md
echo "print('Hello')" > src/main.py

# List everything
find . -type f
```

### Workflow 2: System Exploration
```bash
# Check system
uptime
whoami
users
env

# Explore filesystem
ls /
cd /etc
cat motd
cat hosts

# View logs
tail /var/log/system.log
```

### Workflow 3: Fun Time!
```bash
# Random fun
fortune
cowsay "Time for a break!"
joke
hacker
weather Tokyo
dice 20
flip
```

### Workflow 4: Destruction & Rebirth
```bash
# Create some data
mkdir /tmp/test
echo "data" > /tmp/test/file.txt

# DESTROY IT!
wipe /tmp/test --confirm

# Or go nuclear!
nuke --i-am-absolutely-sure

# System rebuilds automatically!
```

---

## 🚀 Power User Tips

### Aliases
DoubOS includes built-in aliases:
- `ll` = `ls -l` (detailed list)
- `la` = `ls -a` (show hidden)
- `..` = `cd ..` (go up)
- `cls` = `clear` (clear screen)
- `dir` = `ls` (Windows habit)

### Command History
- View history: `history`
- Reuse commands: Use ↑/↓ arrows
- All commands are logged

### Help System
```bash
help              # List all commands
help ls           # Specific command help
man format        # Manual page (same as help)
```

---

## 📊 Statistics

- **Commands**: 50+
- **File Operations**: 13
- **System Commands**: 11
- **Network Tools**: 4
- **Dangerous Commands**: 8
- **Fun Commands**: 13
- **Users**: 3 default
- **Directories**: 14 default

---

## 🎓 Educational Value

DoubOS teaches:
1. **File Systems** - How files and directories work
2. **Users & Permissions** - Authentication and authorization
3. **Shell Commands** - Unix/Linux command-line basics
4. **OS Concepts** - Processes, memory, system calls
5. **Safe Experimentation** - Try destructive commands safely!

---

## 💡 Use Cases

### For Learning
- Understand OS fundamentals
- Practice shell commands
- Learn about file systems

### For Fun
- Play with Easter eggs
- Try dangerous commands safely
- Customize and extend

### For Development
- Test command-line interfaces
- Prototype OS concepts
- Build new features

---

## 🔐 Safety Guarantee

**Everything in DoubOS is VIRTUAL and SAFE:**
- ✅ No real files are touched
- ✅ Your actual system is protected
- ✅ All operations are simulated
- ✅ Instant reset available
- ✅ Persistent only if you save

**You literally cannot break anything!**

---

## 🎉 Summary

DoubOS is a **fully functional operating system simulator** that provides:
- Complete virtual file system
- Multi-user authentication
- 50+ working commands
- Network simulation
- Package management
- Destructive operations (safely!)
- Fun Easter eggs
- Educational value
- Session persistence
- Extensible architecture

**All in pure Python with zero dependencies!**

Start exploring: `python doubos.py`

---

*DoubOS - Where learning meets fun, and destruction is always safe!* 🚀💾
