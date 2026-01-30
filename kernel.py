"""
DoubOS - A Fully Fledged Operating System Simulator
Main Kernel and Shell
"""

import os
import sys
import json
import time
import platform
from datetime import datetime
from typing import Dict, List, Optional, Callable


class DoubOSKernel:
    """Main kernel for DoubOS"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.running = False
        self.current_user = None
        self.boot_time = None
        self.command_history = []
        self.environment_vars = {
            "OS_NAME": "DoubOS",
            "OS_VERSION": "1.0.0",
            "PATH": "/bin:/usr/bin:/sbin",
            "HOME": "/home"
        }
        
    def boot(self):
        """Boot the operating system"""
        self.boot_time = datetime.now()
        self.running = True
        print(f"""
╔══════════════════════════════════════════════════════════╗
║                    DoubOS v{self.version}                    ║
║              Advanced Operating System                   ║
║                                                          ║
║  Warning: This OS includes powerful system commands     ║
║  Use with caution!                                      ║
╚══════════════════════════════════════════════════════════╝

Booting DoubOS...
Initializing kernel... [OK]
Loading file system... [OK]
Starting user management... [OK]
Loading command processor... [OK]

System ready!
""")
        return True
        
    def shutdown(self):
        """Shutdown the operating system"""
        print("\n🔌 Shutting down DoubOS...")
        uptime = datetime.now() - self.boot_time if self.boot_time else None
        if uptime:
            print(f"   Uptime: {uptime}")
        print("   Saving system state... [OK]")
        print("   Goodbye! 👋\n")
        self.running = False
        
    def get_uptime(self) -> str:
        """Get system uptime"""
        if not self.boot_time:
            return "System not booted"
        uptime = datetime.now() - self.boot_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
        
    def get_env(self, var: str) -> Optional[str]:
        """Get environment variable"""
        return self.environment_vars.get(var)
        
    def set_env(self, var: str, value: str):
        """Set environment variable"""
        self.environment_vars[var] = value
        
    def add_to_history(self, command: str):
        """Add command to history"""
        self.command_history.append({
            "command": command,
            "timestamp": datetime.now(),
            "user": self.current_user
        })


class DoubOSShell:
    """Command-line shell for DoubOS"""
    
    def __init__(self, kernel: DoubOSKernel):
        self.kernel = kernel
        self.prompt_symbol = "$"
        self.current_dir = "/"
        
    def get_prompt(self) -> str:
        """Generate command prompt"""
        user = self.kernel.current_user or "guest"
        color_user = "\033[92m"  # Green
        color_dir = "\033[94m"   # Blue
        color_reset = "\033[0m"
        return f"{color_user}{user}{color_reset}@DoubOS:{color_dir}{self.current_dir}{color_reset}{self.prompt_symbol} "
        
    def run(self):
        """Main shell loop"""
        while self.kernel.running:
            try:
                command = input(self.get_prompt()).strip()
                if command:
                    self.kernel.add_to_history(command)
                    yield command
            except KeyboardInterrupt:
                print("\n^C")
                continue
            except EOFError:
                print()
                break
                
    def change_directory(self, path: str):
        """Change current directory"""
        self.current_dir = path
