# DoubOS Command Reference

## 📖 Complete Command Catalog

### 🧭 Navigation Commands (5)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `cd` | Change directory | `cd <path>` | `cd /home/admin` |
| `pwd` | Print working directory | `pwd` | `pwd` |
| `ls` | List directory contents | `ls [-l] [-a] [path]` | `ls -l /etc` |
| `ll` | Alias for `ls -l` | `ll` | `ll` |
| `la` | Alias for `ls -a` | `la` | `la` |

---

### 📁 File Operations (13)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `cat` | Display file contents | `cat <file>` | `cat README.md` |
| `touch` | Create empty file | `touch <file>` | `touch newfile.txt` |
| `mkdir` | Create directory | `mkdir [-p] <dir>` | `mkdir -p /a/b/c` |
| `rm` | Remove files/dirs | `rm [-r] <path>` | `rm -r folder` |
| `cp` | Copy file | `cp <src> <dst>` | `cp file.txt backup.txt` |
| `mv` | Move/rename | `mv <src> <dst>` | `mv old.txt new.txt` |
| `echo` | Print text | `echo <text>` | `echo "Hello"` |
| `grep` | Search in file | `grep <pattern> <file>` | `grep "error" log.txt` |
| `find` | Find files | `find <path> -name <pattern>` | `find /home -name "*.txt"` |
| `head` | First lines of file | `head [-n N] <file>` | `head -n 5 file.txt` |
| `tail` | Last lines of file | `tail [-n N] <file>` | `tail -n 10 log.txt` |
| `wc` | Count words/lines | `wc <file>` | `wc document.txt` |
| `tar` | Archive files | `tar -czf <archive> <files>` | `tar -czf backup.tar.gz *` |

---

### 💻 System Commands (11)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `clear` | Clear screen | `clear` | `clear` |
| `date` | Show date/time | `date` | `date` |
| `uptime` | System uptime | `uptime` | `uptime` |
| `whoami` | Current user | `whoami` | `whoami` |
| `uname` | System info | `uname [-a]` | `uname -a` |
| `history` | Command history | `history` | `history` |
| `env` | Environment vars | `env` | `env` |
| `df` | Disk usage | `df` | `df` |
| `ps` | Process list | `ps` | `ps` |
| `top` | System monitor | `top` | `top` |
| `ifconfig` | Network config | `ifconfig` | `ifconfig` |

---

### 👥 User Management (3)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `users` | List all users | `users` | `users` |
| `passwd` | Change password | `passwd` | `passwd` |
| `su` | Switch user | `su [user]` | `su root` |

---

### 🌐 Network Simulation (4)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `ping` | Ping host | `ping <host>` | `ping google.com` |
| `wget` | Download file | `wget <url>` | `wget http://example.com/file.zip` |
| `curl` | Fetch URL | `curl <url>` | `curl http://api.example.com` |
| `ifconfig` | Network interfaces | `ifconfig` | `ifconfig` |

---

### 📦 Package Manager (1)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `apt` | Package manager | `apt <action> <package>` | `apt install nginx` |

**APT Actions:**
- `update` - Update package lists
- `upgrade` - Upgrade packages
- `install <pkg>` - Install package
- `remove <pkg>` - Remove package

---

### 🔐 Permissions (2)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `chmod` | Change permissions | `chmod <mode> <file>` | `chmod 755 script.sh` |
| `chown` | Change owner | `chown <owner> <file>` | `chown admin file.txt` |

---

### ⚡ Power Commands (3)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `shutdown` | Shutdown system | `shutdown` | `shutdown` |
| `reboot` | Reboot system | `reboot` | `reboot` |
| `exit` | Exit shell | `exit` | `exit` |

---

### ☢️ DANGEROUS Commands (8) - Admin Only!

| Command | Description | Confirmation Required | Impact |
|---------|-------------|----------------------|--------|
| `format` | **Wipe filesystem** | `--confirm` | Destroys ALL files |
| `nuke` | **Total annihilation** | `--i-am-absolutely-sure` | Destroys EVERYTHING |
| `shred` | Secure file deletion | No | Overwrites & deletes file |
| `wipe` | Destroy directory | `--confirm` | Deletes dir & contents |
| `corrupt` | Corrupt file data | No | Makes file unreadable |
| `forkbomb` | Process explosion | No | Simulates system crash |
| `logbomb` | Flood logs | No | Fills log files |
| `killall` | Kill all processes | `--confirm` | Terminates everything |

⚠️ **WARNING**: These commands are destructive but SAFE (virtual only)!

**Examples:**
```bash
format --confirm                      # Wipe everything
nuke --i-am-absolutely-sure          # Nuclear option
shred secret.txt                      # Secure delete
wipe /tmp/old --confirm              # Delete directory
corrupt document.txt                  # Corrupt file
```

---

### 🎉 Fun Commands (13)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `cowsay` | 🐮 ASCII cow | `cowsay <message>` | `cowsay "Moo!"` |
| `fortune` | 🔮 Random fortune | `fortune` | `fortune` |
| `joke` | 😄 Programming joke | `joke` | `joke` |
| `quote` | 💭 Inspiring quote | `quote` | `quote` |
| `hacker` | 👨‍💻 Hacker mode | `hacker` | `hacker` |
| `matrix` | 🟢 Enter Matrix | `matrix` | `matrix` |
| `ascii` | 🎨 DoubOS art | `ascii` | `ascii` |
| `snake` | 🐍 ASCII snake | `snake` | `snake` |
| `banner` | 📢 Text banner | `banner <text>` | `banner "DoubOS"` |
| `dice` | 🎲 Roll dice | `dice [sides]` | `dice 20` |
| `flip` | 🪙 Flip coin | `flip` | `flip` |
| `weather` | 🌤️ Weather report | `weather [city]` | `weather Tokyo` |
| `colors` | 🎨 Color palette | `colors` | `colors` |

---

### ❓ Help & Documentation (3)

| Command | Description | Usage | Example |
|---------|-------------|-------|---------|
| `help` | List commands / get help | `help [command]` | `help ls` |
| `man` | Manual page (same as help) | `man <command>` | `man grep` |
| `alias` | Show command aliases | `alias` | `alias` |

---

## 🔗 Command Aliases

Built-in shortcuts:

| Alias | Expands To | Description |
|-------|-----------|-------------|
| `ll` | `ls -l` | Detailed list |
| `la` | `ls -a` | Show hidden files |
| `..` | `cd ..` | Go up one directory |
| `cls` | `clear` | Clear screen (Windows habit) |
| `dir` | `ls` | List directory (Windows habit) |

---

## 📊 Command Statistics

- **Total Commands**: 50+
- **Navigation**: 5
- **File Operations**: 13
- **System**: 11
- **Users**: 3
- **Network**: 4
- **Package Manager**: 1
- **Permissions**: 2
- **Power**: 3
- **Dangerous**: 8
- **Fun**: 13
- **Help**: 3

---

## 🎯 Common Workflows

### Workflow 1: File Management
```bash
mkdir project               # Create directory
cd project                  # Enter it
touch README.md            # Create file
echo "# Project" > README.md  # Write to file
cat README.md              # View file
ls -l                      # List files
```

### Workflow 2: System Exploration
```bash
whoami                     # Who am I?
pwd                        # Where am I?
uptime                     # How long running?
users                      # Who else exists?
history                    # What have I done?
```

### Workflow 3: Search & Analysis
```bash
find /home -name "*.txt"   # Find text files
grep "error" /var/log/system.log  # Find errors
wc document.txt           # Count words
head -n 20 file.txt       # First 20 lines
tail -n 10 log.txt        # Last 10 lines
```

### Workflow 4: Network Operations
```bash
ping google.com           # Test connectivity
wget http://example.com/file.zip  # Download
curl http://api.example.com       # Fetch data
ifconfig                  # Check network
```

### Workflow 5: Package Management
```bash
apt update                # Update lists
apt install nginx         # Install package
apt upgrade              # Upgrade all
apt remove nginx         # Remove package
```

---

## 💡 Pro Tips

### Tip 1: Use Tab Completion
Most terminals support tab completion for commands

### Tip 2: Command History
Use ↑ and ↓ arrows to navigate command history

### Tip 3: Quick Navigation
```bash
cd ~          # Go to home directory
cd ..         # Go up one level
cd -          # Go to previous directory
pwd           # Check where you are
```

### Tip 4: Batch Operations
```bash
rm -r folder1 folder2 folder3    # Remove multiple
cp *.txt backup/                 # Copy all .txt files
```

### Tip 5: Get Help Anytime
```bash
help              # List all commands
help <command>    # Get specific help
man <command>     # Same as help
```

---

## 🚀 Quick Reference Card

**Most Used Commands:**
```
ls    cd    pwd   cat   mkdir   rm    cp    mv
help  exit  clear whoami uptime users history
```

**File Operations:**
```
touch  cat  echo  grep  find  head  tail  wc
```

**Fun Stuff:**
```
fortune  cowsay  joke  hacker  matrix  weather
```

**Dangerous (Admin):**
```
format  nuke  shred  wipe  corrupt
```

---

## 📚 Learning Path

### Level 1: Beginner
Start with: `pwd`, `ls`, `cd`, `cat`, `whoami`, `help`

### Level 2: Intermediate  
Learn: `mkdir`, `touch`, `echo`, `cp`, `mv`, `rm`, `grep`, `find`

### Level 3: Advanced
Master: `chmod`, `chown`, `tar`, `wget`, `apt`, Network commands

### Level 4: Expert
Experiment: `format`, `nuke`, `shred`, `wipe`, All dangerous commands

---

**Remember**: Type `help` anytime for command list!

**Have Fun!** 🎉
