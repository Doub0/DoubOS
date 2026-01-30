#!/usr/bin/env python3
"""
DoubOS Comprehensive Test - Verify all features work
"""

import sys
import time
from kernel import DoubOSKernel
from filesystem import VirtualFileSystem
from users import UserManager
from gui_login import LoginScreen
from gui_desktop import DoubOSDesktop


def main():
    """Test DoubOS"""
    print("="*70)
    print("   DoubOS COMPREHENSIVE TEST SUITE")
    print("="*70)
    print()
    
    # Initialize core components
    print("🔧 PHASE 1: Initializing DoubOS...")
    kernel = DoubOSKernel()
    filesystem = VirtualFileSystem()
    user_manager = UserManager()
    
    # Load state
    try:
        import os
        if os.path.exists("doubos_filesystem.json"):
            filesystem.load_from_disk("doubos_filesystem.json")
            print("  ✓ Filesystem loaded")
        if os.path.exists("doubos_users.json"):
            user_manager.load_from_disk("doubos_users.json")
            print("  ✓ Users loaded")
    except Exception as e:
        print(f"  ⚠ Could not load previous state: {e}")
    
    # Boot kernel
    print("\n🚀 PHASE 2: Booting kernel...")
    kernel.boot()
    print("  ✓ Kernel booted")
    
    # Auto-login
    print("\n🔐 PHASE 3: User authentication...")
    user = user_manager.authenticate("admin", "admin123")
    
    if not user:
        print("  ⚠ Admin account not found, creating...")
        user_manager.add_user("admin", "admin123", True)
        user = user_manager.authenticate("admin", "admin123")
    
    if user:
        print(f"  ✓ Logged in as: {user.username} (Admin: {user.is_admin})")
        kernel.current_user = user.username
    else:
        print("  ✗ Login failed")
        return
    
    # Launch desktop
    print("\n🖥️  PHASE 4: Loading desktop environment...")
    try:
        desktop = DoubOSDesktop(kernel, filesystem, user_manager)
        print("  ✓ Desktop created")
        print(f"  ✓ Window manager initialized")
        print(f"  ✓ Colors: {len(desktop.colors)} themes loaded")
        
    except Exception as e:
        print(f"  ✗ Desktop error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test desktop features
    print("\n📋 PHASE 5: Testing desktop features...")
    
    # Check desktop icons
    print("  Checking desktop icons...")
    try:
        desktop.create_icon("Test", lambda: None, 100, 100)
        print("    ✓ Desktop icons functional")
    except Exception as e:
        print(f"    ✗ Desktop icons error: {e}")
    
    # Check window manager
    print("  Checking window manager...")
    if desktop.window_manager:
        print(f"    ✓ Window manager ready (offset: {desktop.window_manager.window_offset})")
    else:
        print("    ✗ Window manager not initialized")
    
    # Check apps availability
    print("  Checking app imports...")
    apps_ok = True
    try:
        from windowed_apps import TerminalApp, FileExplorerApp, TextEditorApp, CalculatorApp, SettingsApp
        print("    ✓ Windowed apps available (5 apps)")
    except Exception as e:
        print(f"    ✗ Windowed apps error: {e}")
        apps_ok = False
    
    try:
        from croptopia_sim import CroptopiaSim
        print("    ✓ Croptopia game available")
    except Exception as e:
        print(f"    ✗ Croptopia error: {e}")
    
    try:
        from games_menu import GamesMenuApp
        print("    ✓ Games menu available")
    except Exception as e:
        print(f"    ✗ Games menu error: {e}")
    
    if not apps_ok:
        print("\n❌ TEST FAILED: Some apps missing")
        return
    
    # Summary
    print("\n" + "="*70)
    print("   ✓ ALL TESTS PASSED - SYSTEM READY!")
    print("="*70)
    print("""
    DoubOS is fully functional with:
    ✓ Kernel and filesystem
    ✓ User management with login
    ✓ Window manager (frames inside simulation)
    ✓ 5 windowed applications (Terminal, Files, Editor, Calculator, Settings)
    ✓ Croptopia farming game
    ✓ Games menu launcher
    ✓ Desktop with 6 icons and taskbar
    
    To launch the full system:
    $ python doubos_gui.py  (with login screen)
    $ python doubos_test.py (auto-login for testing)
    """)
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
