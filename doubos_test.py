#!/usr/bin/env python3
"""
DoubOS Quick Test Launcher - Auto login
"""

import sys
from kernel import DoubOSKernel
from filesystem import VirtualFileSystem
from users import UserManager
from gui_desktop import DoubOSDesktop


def main():
    """Main GUI launcher"""
    print("="*60)
    print("   DoubOS - Quick Test Launcher")
    print("="*60)
    print()
    
    # Initialize core components
    print("🔧 Initializing DoubOS...")
    kernel = DoubOSKernel()
    filesystem = VirtualFileSystem()
    user_manager = UserManager()
    
    # Try to load previous state
    try:
        import os
        if os.path.exists("doubos_filesystem.json"):
            filesystem.load_from_disk("doubos_filesystem.json")
            print("✓ Filesystem loaded")
        if os.path.exists("doubos_users.json"):
            user_manager.load_from_disk("doubos_users.json")
            print("✓ Users loaded")
    except Exception as e:
        print(f"⚠️ Could not load previous state: {e}")
    
    # Boot kernel
    print("\n🚀 Booting DoubOS kernel...")
    kernel.boot()
    
    # Auto-login as admin (for testing)
    print("\n✓ Auto-logging in as admin...")
    user = user_manager.authenticate("admin", "admin123")
    
    if not user:
        # Create admin if it doesn't exist
        print("  Creating admin account...")
        user_manager.add_user("admin", "admin123", True)
        user = user_manager.authenticate("admin", "admin123")
    
    if not user:
        print("❌ Login failed")
        return
        
    # Login successful
    kernel.current_user = user.username
    print(f"✓ Logged in as: {user.username}")
    
    # Launch desktop
    print("🖥️ Loading desktop environment...")
    desktop = DoubOSDesktop(kernel, filesystem, user_manager)
    
    print("\n🎉 DoubOS Desktop ready!\n")
    print("💡 Try clicking the desktop icons or START menu to open apps\n")
    
    # Run desktop
    try:
        desktop.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Desktop error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Save state
        print("\n💾 Saving system state...")
        try:
            filesystem.save_to_disk("doubos_filesystem.json")
            user_manager.save_to_disk("doubos_users.json")
            print("✓ State saved")
        except Exception as e:
            print(f"⚠️ Error saving: {e}")
            
        print("\n👋 DoubOS shutdown complete.\n")


if __name__ == "__main__":
    main()
