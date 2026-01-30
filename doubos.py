"""
DoubOS - Main Entry Point
Fully Fledged Operating System Simulator

Run this file to start DoubOS!
"""

import sys
import os
from kernel import DoubOSKernel, DoubOSShell
from filesystem import VirtualFileSystem
from users import UserManager
from commands import CommandProcessor, CommandContext
from dangerous_commands import register_dangerous_commands
from utilities import register_utility_commands
from fun_commands import register_fun_commands


class DoubOS:
    """Main DoubOS orchestrator"""
    
    def __init__(self):
        # Initialize core components
        self.kernel = DoubOSKernel()
        self.filesystem = VirtualFileSystem()
        self.user_manager = UserManager()
        self.shell = DoubOSShell(self.kernel)
        
        # Create command context
        self.context = CommandContext(
            self.kernel,
            self.filesystem,
            self.user_manager,
            self.shell
        )
        
        # Initialize command processor
        self.processor = CommandProcessor(self.context)
        
        # Register additional commands
        register_dangerous_commands(self.processor)
        register_utility_commands(self.processor)
        register_fun_commands(self.processor)
        
        # Store processor reference in context
        self.context.commands = self.processor.commands
        
    def login_screen(self):
        """Display login screen and handle authentication"""
        print("\n" + "="*60)
        print("DoubOS Login")
        print("="*60)
        print("\nDefault users:")
        print("  • root (admin)   - password: root123")
        print("  • admin (admin)  - password: admin123")
        print("  • guest          - password: guest")
        print("\nType 'exit' to quit\n")
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                username = input("Username: ").strip()
                
                if username.lower() == 'exit':
                    return False
                    
                password = input("Password: ").strip()
                
                if self.user_manager.login(username, password):
                    user = self.user_manager.get_current_user()
                    self.kernel.current_user = username
                    self.context.current_dir = user.home_dir
                    self.shell.current_dir = user.home_dir
                    
                    print(f"\n✓ Login successful! Welcome, {username}!")
                    
                    # Show message of the day
                    motd = self.filesystem.read_file("/etc/motd")
                    if motd:
                        print(f"\n{motd}")
                    
                    return True
                else:
                    attempts += 1
                    remaining = max_attempts - attempts
                    if remaining > 0:
                        print(f"❌ Login failed. {remaining} attempt(s) remaining.\n")
                    else:
                        print("❌ Too many failed attempts. Exiting.")
                        return False
                        
            except KeyboardInterrupt:
                print("\n\n⚠️  Login cancelled.")
                return False
            except EOFError:
                print()
                return False
                
        return False
        
    def run(self):
        """Main run loop"""
        # Boot the system
        self.kernel.boot()
        
        # Login
        if not self.login_screen():
            print("\n👋 Goodbye!\n")
            return
            
        print("\nType 'help' for a list of commands")
        print("Type 'exit' or 'shutdown' to quit\n")
        
        # Main shell loop
        for command in self.shell.run():
            if command:
                output = self.processor.execute(command)
                if output:
                    print(output)
                    
                # Check if kernel was shutdown
                if not self.kernel.running:
                    break
                    
    def save_state(self):
        """Save system state to disk"""
        try:
            self.filesystem.save_to_disk("doubos_filesystem.json")
            self.user_manager.save_to_disk("doubos_users.json")
            print("✓ System state saved")
        except Exception as e:
            print(f"⚠️  Error saving state: {e}")
            
    def load_state(self):
        """Load system state from disk"""
        try:
            if os.path.exists("doubos_filesystem.json"):
                self.filesystem.load_from_disk("doubos_filesystem.json")
                print("✓ Filesystem loaded from disk")
                
            if os.path.exists("doubos_users.json"):
                self.user_manager.load_from_disk("doubos_users.json")
                print("✓ Users loaded from disk")
        except Exception as e:
            print(f"⚠️  Error loading state: {e}")


def main():
    """Main entry point"""
    print("\033[92m")  # Green color
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   ██████╗  ██████╗ ██╗   ██╗██████╗  ██████╗ ███████╗║
    ║   ██╔══██╗██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔════╝║
    ║   ██║  ██║██║   ██║██║   ██║██████╔╝██║   ██║███████╗║
    ║   ██║  ██║██║   ██║██║   ██║██╔══██╗██║   ██║╚════██║║
    ║   ██████╔╝╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝███████║║
    ║   ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝║
    ║                                                       ║
    ║          A Fully Fledged Operating System            ║
    ║                 Virtual Edition                      ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    print("\033[0m")  # Reset color
    
    # Create and run DoubOS
    os_instance = DoubOS()
    
    # Optionally load previous state
    load_previous = input("Load previous session? (y/n): ").strip().lower()
    if load_previous == 'y':
        os_instance.load_state()
    
    try:
        os_instance.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Save state on exit
        save = input("\nSave session for next time? (y/n): ").strip().lower()
        if save == 'y':
            os_instance.save_state()
            
        print("\n💾 DoubOS shutdown complete.\n")


if __name__ == "__main__":
    main()
