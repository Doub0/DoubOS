"""
DoubOS Demo Script
Showcases various features and commands

This script can be used to demonstrate DoubOS capabilities
"""


def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def demo_basic_commands():
    """Demo basic file operations"""
    print_section("Basic File Operations")
    
    commands = [
        ("pwd", "Show current directory"),
        ("ls /", "List root directory"),
        ("cat /etc/motd", "View message of the day"),
        ("whoami", "Show current user"),
        ("uptime", "System uptime"),
    ]
    
    print("Try these commands:\n")
    for cmd, desc in commands:
        print(f"  {cmd:30} # {desc}")


def demo_file_system():
    """Demo file system operations"""
    print_section("File System Demo")
    
    commands = [
        ("mkdir /tmp/demo", "Create directory"),
        ("cd /tmp/demo", "Change to directory"),
        ("echo 'Hello DoubOS!' > test.txt", "Create file"),
        ("cat test.txt", "View file"),
        ("ls -l", "List files with details"),
        ("cp test.txt backup.txt", "Copy file"),
        ("rm test.txt", "Delete file"),
    ]
    
    print("File system operations:\n")
    for cmd, desc in commands:
        print(f"  {cmd:40} # {desc}")


def demo_fun_commands():
    """Demo fun commands"""
    print_section("Fun Commands")
    
    commands = [
        ("fortune", "Get a random fortune"),
        ("cowsay 'DoubOS is awesome!'", "Make cow say something"),
        ("joke", "Tell a programming joke"),
        ("hacker", "Enter hacker mode"),
        ("matrix", "Enter the Matrix"),
        ("weather London", "Check weather"),
        ("dice 20", "Roll a 20-sided die"),
        ("flip", "Flip a coin"),
        ("ascii", "DoubOS ASCII art"),
    ]
    
    print("Fun commands to try:\n")
    for cmd, desc in commands:
        print(f"  {cmd:40} # {desc}")


def demo_utilities():
    """Demo utility commands"""
    print_section("Utility Commands")
    
    commands = [
        ("ping google.com", "Ping a host"),
        ("wget http://example.com/file.txt", "Download file"),
        ("grep 'pattern' file.txt", "Search in file"),
        ("find /home -name '*.txt'", "Find files"),
        ("history", "View command history"),
        ("users", "List all users"),
        ("env", "Show environment variables"),
    ]
    
    print("Utility commands:\n")
    for cmd, desc in commands:
        print(f"  {cmd:40} # {desc}")


def demo_dangerous_commands():
    """Demo dangerous commands (with warnings)"""
    print_section("⚠️  DANGEROUS COMMANDS ⚠️")
    
    print("These commands are DESTRUCTIVE (but safe in DoubOS!):\n")
    
    commands = [
        ("format --confirm", "Wipe entire file system"),
        ("nuke --i-am-absolutely-sure", "Total system annihilation"),
        ("shred secret.txt", "Securely delete file"),
        ("wipe /tmp/folder --confirm", "Destroy directory"),
        ("corrupt file.txt", "Corrupt file data"),
        ("forkbomb", "Process explosion"),
        ("logbomb", "Flood logs"),
        ("killall --confirm", "Kill all processes"),
    ]
    
    for cmd, desc in commands:
        print(f"  ⚠️  {cmd:37} # {desc}")
    
    print("\n⚠️  Remember: All operations are virtual and safe!")


def demo_admin_features():
    """Demo admin-only features"""
    print_section("Admin Features")
    
    commands = [
        ("apt update", "Update package lists"),
        ("apt install nginx", "Install package"),
        ("chown user file.txt", "Change file owner"),
        ("killall --confirm", "Kill all processes"),
        ("format --confirm", "Format filesystem"),
    ]
    
    print("Admin-only commands (requires admin login):\n")
    for cmd, desc in commands:
        print(f"  🔒 {cmd:37} # {desc}")


def demo_help_system():
    """Demo help system"""
    print_section("Help System")
    
    print("""
DoubOS has extensive built-in help:

  help                    # List all commands
  help <command>          # Get help for specific command
  man <command>           # Same as help

Example:
  help ls                 # Get help for ls command
  help format             # See format command details
""")


def main():
    """Main demo"""
    print("\033[92m")  # Green
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║          DoubOS Interactive Demo Guide               ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    print("\033[0m")  # Reset
    
    print("""
Welcome to DoubOS Demo!

This guide shows you what DoubOS can do. 
Each section demonstrates different features.

To actually run these commands, start DoubOS:
    python doubos.py

Then login with:
    Username: admin
    Password: admin123
""")
    
    input("Press Enter to see the demo...")
    
    demo_basic_commands()
    input("\nPress Enter for next section...")
    
    demo_file_system()
    input("\nPress Enter for next section...")
    
    demo_fun_commands()
    input("\nPress Enter for next section...")
    
    demo_utilities()
    input("\nPress Enter for next section...")
    
    demo_admin_features()
    input("\nPress Enter for next section...")
    
    demo_dangerous_commands()
    input("\nPress Enter for next section...")
    
    demo_help_system()
    
    print_section("Ready to Start!")
    
    print("""
You're ready to explore DoubOS!

To start:
    python doubos.py

Quick tips:
  • Type 'help' anytime for command list
  • Try 'fortune' for random fortunes
  • Use 'cowsay' for ASCII fun
  • All destructive commands are SAFE!

Have fun exploring! 🚀
""")


if __name__ == "__main__":
    main()
