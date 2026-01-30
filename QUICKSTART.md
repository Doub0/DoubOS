# DoubOS Quick Start Guide

## Installation

1. Ensure Python 3.7+ is installed
2. Download all DoubOS files to a folder
3. Run: `python doubos.py`

## First Login

Use one of these accounts:
- `root` / `root123` - Full admin
- `admin` / `admin123` - Admin user  
- `guest` / `guest` - Regular user

## Essential Commands

### Getting Started
```bash
help            # List all commands
help <command>  # Get help for specific command
pwd             # Show current directory
ls              # List files
cd <dir>        # Change directory
```

### File Operations
```bash
cat <file>      # View file
echo "text" > file.txt   # Create file
mkdir <dir>     # Create directory
rm <file>       # Delete file
cp <src> <dst>  # Copy file
mv <src> <dst>  # Move/rename
```

### System Info
```bash
whoami          # Current user
uptime          # System uptime
users           # List all users
df              # Disk usage
history         # Command history
```

### Fun Stuff
```bash
fortune         # Random fortune
cowsay <text>   # ASCII cow
joke            # Programming joke
hacker          # 1337 mode
matrix          # Enter the Matrix
weather         # Weather report
```

### Dangerous (Admin Only) ⚠️
```bash
format --confirm              # Wipe filesystem
nuke --i-am-absolutely-sure   # Destroy everything
shred <file>                  # Securely delete file
wipe <dir> --confirm          # Delete directory
```

### Exit
```bash
exit            # Exit DoubOS
shutdown        # Shutdown system
```

## Tips

- Use Tab for command completion (if your terminal supports it)
- Use `!!` to repeat last command
- Type `clear` to clear screen
- Session can be saved on exit
- All destructive commands are SAFE (virtual only!)

## Quick Demo

```bash
# Login
Username: admin
Password: admin123

# Explore
admin@DoubOS:/home/admin$ ls /
admin@DoubOS:/home/admin$ cat /etc/motd

# Create something
admin@DoubOS:/home/admin$ echo "My first file" > test.txt
admin@DoubOS:/home/admin$ cat test.txt

# Have fun
admin@DoubOS:/home/admin$ fortune
admin@DoubOS:/home/admin$ cowsay "DoubOS rocks!"

# Exit
admin@DoubOS:/home/admin$ exit
```

Enjoy DoubOS! 🚀
