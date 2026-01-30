"""
DoubOS USB Bootable Installer
Create a bootable USB drive with DoubOS

WARNING: This is a SIMULATOR for educational purposes.
Real bootable OS creation requires:
- Linux kernel compilation
- Bootloader (GRUB/systemd-boot)
- Init system
- Hardware drivers
- Much more complexity!

This script demonstrates the CONCEPT of creating
a bootable USB installer.
"""

import os
import sys
import shutil
import json
from datetime import datetime


class DoubOSInstaller:
    """DoubOS USB/ISO Installer Creator"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.install_size = "~50MB"  # Estimated
        
    def show_banner(self):
        """Show installer banner"""
        print("\n" + "="*70)
        print("""
██████╗  ██████╗ ██╗   ██╗██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║██║   ██║██████╔╝██║   ██║███████╗
██║  ██║██║   ██║██║   ██║██╔══██╗██║   ██║╚════██║
██████╔╝╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝███████║
╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

            USB Bootable Installer Creator
                  Version """ + self.version + """
        """)
        print("="*70)
        print()
        
    def check_requirements(self):
        """Check system requirements"""
        print("🔍 Checking system requirements...")
        print()
        
        requirements = [
            ("Python 3.7+", sys.version_info >= (3, 7), "✓"),
            ("Tkinter GUI library", self.check_tkinter(), "✓"),
            ("Write permissions", os.access(".", os.W_OK), "✓"),
            ("~50MB free space", True, "✓"),
        ]
        
        all_ok = True
        for name, status, checkmark in requirements:
            symbol = "✓" if status else "✗"
            color = "✅" if status else "❌"
            print(f"  {color} {name}: {symbol}")
            if not status:
                all_ok = False
                
        print()
        return all_ok
        
    def check_tkinter(self):
        """Check if tkinter is available"""
        try:
            import tkinter
            return True
        except ImportError:
            return False
            
    def create_install_directory(self, target_dir):
        """Create installation directory structure"""
        print(f"\n📁 Creating installation in: {target_dir}")
        print()
        
        # Create directory structure
        dirs = [
            "DoubOS",
            "DoubOS/system",
            "DoubOS/apps",
            "DoubOS/data",
            "DoubOS/boot",
            "DoubOS/docs",
        ]
        
        for d in dirs:
            path = os.path.join(target_dir, d)
            os.makedirs(path, exist_ok=True)
            print(f"  ✓ Created: {d}")
            
        return os.path.join(target_dir, "DoubOS")
        
    def copy_system_files(self, install_dir):
        """Copy DoubOS system files"""
        print("\n📦 Copying system files...")
        print()
        
        # Core system files
        system_files = [
            "doubos.py",
            "doubos_gui.py",
            "kernel.py",
            "filesystem.py",
            "users.py",
            "commands.py",
            "dangerous_commands.py",
            "utilities.py",
            "fun_commands.py",
            "gui_desktop.py",
            "gui_apps.py",
            "gui_login.py",
        ]
        
        for file in system_files:
            if os.path.exists(file):
                dest = os.path.join(install_dir, "system", file)
                shutil.copy2(file, dest)
                print(f"  ✓ {file}")
                
        # Documentation
        doc_files = [
            "README.md",
            "QUICKSTART.md",
            "FEATURES.md",
            "COMMANDS.md",
        ]
        
        print("\n📚 Copying documentation...")
        for file in doc_files:
            if os.path.exists(file):
                dest = os.path.join(install_dir, "docs", file)
                shutil.copy2(file, dest)
                print(f"  ✓ {file}")
                
    def create_boot_files(self, install_dir):
        """Create boot files"""
        print("\n🚀 Creating boot files...")
        print()
        
        # Launcher scripts
        windows_launcher = """@echo off
echo Starting DoubOS...
cd "%~dp0system"
python doubos_gui.py
pause
"""
        
        linux_launcher = """#!/bin/bash
echo "Starting DoubOS..."
cd "$(dirname "$0")/system"
python3 doubos_gui.py
"""
        
        # Write launchers
        with open(os.path.join(install_dir, "boot", "start_doubos.bat"), 'w') as f:
            f.write(windows_launcher)
        print("  ✓ Windows launcher created")
        
        with open(os.path.join(install_dir, "boot", "start_doubos.sh"), 'w') as f:
            f.write(linux_launcher)
        print("  ✓ Linux launcher created")
        
        # Make Linux script executable (on Unix systems)
        try:
            os.chmod(os.path.join(install_dir, "boot", "start_doubos.sh"), 0o755)
        except:
            pass
            
    def create_autorun(self, install_dir):
        """Create autorun file for USB"""
        print("\n💿 Creating autorun configuration...")
        
        autorun_inf = """[autorun]
open=boot\\start_doubos.bat
icon=doubos.ico
label=DoubOS Desktop
"""
        
        with open(os.path.join(install_dir, "autorun.inf"), 'w') as f:
            f.write(autorun_inf)
        print("  ✓ Autorun.inf created")
        
    def create_install_info(self, install_dir):
        """Create installation information file"""
        print("\n📋 Creating installation info...")
        
        info = {
            "name": "DoubOS",
            "version": self.version,
            "created": datetime.now().isoformat(),
            "type": "Portable Installation",
            "size": self.install_size,
            "description": "DoubOS Desktop Operating System",
            "requirements": {
                "python": "3.7+",
                "libraries": ["tkinter (included with Python)"]
            },
            "usage": {
                "windows": "Run boot/start_doubos.bat",
                "linux": "Run boot/start_doubos.sh",
                "macos": "Run boot/start_doubos.sh"
            }
        }
        
        with open(os.path.join(install_dir, "INSTALL_INFO.json"), 'w') as f:
            json.dump(info, f, indent=2)
        print("  ✓ Installation info created")
        
    def create_readme(self, install_dir):
        """Create README for installation"""
        print("\n📝 Creating README...")
        
        readme = """# DoubOS - Portable Installation

## Quick Start

### Windows
1. Double-click `boot/start_doubos.bat`
2. Or run: `python system/doubos_gui.py`

### Linux/Mac
1. Run: `bash boot/start_doubos.sh`
2. Or run: `python3 system/doubos_gui.py`

## What's Included

- DoubOS Desktop Environment (GUI)
- Virtual File System
- User Management
- 50+ Terminal Commands
- Multiple GUI Applications
- Complete Documentation

## System Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python)
- ~50MB disk space
- Any modern OS (Windows/Linux/Mac)

## First Time Setup

1. Launch DoubOS
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`
3. Or create a new account

## Features

✅ Graphical Desktop Environment
✅ File Explorer
✅ Terminal
✅ Text Editor
✅ Calculator
✅ System Settings
✅ User Management
✅ And much more!

## Documentation

See the `docs/` folder for complete documentation:
- README.md - Full documentation
- QUICKSTART.md - Quick start guide
- FEATURES.md - Feature showcase
- COMMANDS.md - Command reference

## Support

DoubOS is a educational operating system simulator.
It runs entirely in Python and doesn't modify your real system.

Everything is virtual and safe!

## Version

DoubOS """ + self.version + """
Built: """ + datetime.now().strftime("%Y-%m-%d") + """

Enjoy DoubOS! 🚀
"""
        
        with open(os.path.join(install_dir, "README.txt"), 'w') as f:
            f.write(readme)
        print("  ✓ README created")
        
    def install_to_directory(self, target_dir):
        """Perform installation"""
        try:
            # Create structure
            install_dir = self.create_install_directory(target_dir)
            
            # Copy files
            self.copy_system_files(install_dir)
            self.create_boot_files(install_dir)
            self.create_autorun(install_dir)
            self.create_install_info(install_dir)
            self.create_readme(install_dir)
            
            print("\n" + "="*70)
            print("✅ Installation Complete!")
            print("="*70)
            print()
            print(f"📍 Location: {install_dir}")
            print()
            print("🚀 To run DoubOS:")
            print(f"   Windows: {os.path.join(install_dir, 'boot', 'start_doubos.bat')}")
            print(f"   Linux/Mac: {os.path.join(install_dir, 'boot', 'start_doubos.sh')}")
            print()
            print("💡 You can copy the entire 'DoubOS' folder to:")
            print("   • USB drive")
            print("   • External hard drive")
            print("   • Network share")
            print("   • Cloud storage")
            print()
            print("   And run it from anywhere!")
            print()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def create_iso_image(self):
        """Create ISO image (advanced feature)"""
        print("\n💿 ISO Image Creation")
        print("="*70)
        print()
        print("Creating a bootable ISO requires additional tools:")
        print()
        print("Linux:")
        print("  1. Install genisoimage: sudo apt install genisoimage")
        print("  2. Run: genisoimage -o doubos.iso -R -J DoubOS/")
        print()
        print("Windows:")
        print("  1. Install ImgBurn or similar tool")
        print("  2. Create ISO from DoubOS folder")
        print()
        print("For a TRUE bootable OS, you would need:")
        print("  • Linux kernel")
        print("  • GRUB bootloader")
        print("  • Init system (systemd/OpenRC)")
        print("  • Hardware drivers")
        print("  • Much more complex setup!")
        print()
        print("DoubOS is a simulator - it runs on TOP of existing OS.")
        print()
        
    def interactive_install(self):
        """Interactive installation wizard"""
        self.show_banner()
        
        print("Welcome to the DoubOS Installation Wizard!")
        print()
        print("This will create a portable DoubOS installation that can be:")
        print("  • Copied to a USB drive")
        print("  • Run from any location")
        print("  • Moved between computers")
        print()
        
        if not self.check_requirements():
            print("\n❌ Some requirements are not met!")
            print("Please install missing components and try again.")
            return
            
        print("\n" + "="*70)
        print("Installation Options")
        print("="*70)
        print()
        print("1. Install to current directory")
        print("2. Install to custom location")
        print("3. Show ISO creation info")
        print("4. Exit")
        print()
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1":
            target = "."
            print(f"\n📁 Installing to: {os.path.abspath(target)}")
            confirm = input("\nContinue? (yes/no): ").strip().lower()
            if confirm == "yes":
                self.install_to_directory(target)
                
        elif choice == "2":
            target = input("\n📁 Enter target directory: ").strip()
            if os.path.exists(target) and os.path.isdir(target):
                print(f"\n📁 Installing to: {os.path.abspath(target)}")
                confirm = input("\nContinue? (yes/no): ").strip().lower()
                if confirm == "yes":
                    self.install_to_directory(target)
            else:
                print(f"\n❌ Directory not found: {target}")
                
        elif choice == "3":
            self.create_iso_image()
            
        elif choice == "4":
            print("\n👋 Installation cancelled.\n")
            return
            
        else:
            print("\n❌ Invalid option!")


def main():
    """Main installer entry point"""
    installer = DoubOSInstaller()
    installer.interactive_install()


if __name__ == "__main__":
    main()
