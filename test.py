"""
DoubOS Test Suite
Quick tests to verify all components work
"""

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from kernel import DoubOSKernel, DoubOSShell
        from filesystem import VirtualFileSystem
        from users import UserManager
        from commands import CommandProcessor, CommandContext
        from dangerous_commands import register_dangerous_commands
        from utilities import register_utility_commands
        from fun_commands import register_fun_commands
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_kernel():
    """Test kernel initialization"""
    print("\nTesting kernel...")
    try:
        from kernel import DoubOSKernel
        kernel = DoubOSKernel()
        kernel.boot()
        assert kernel.running == True
        assert kernel.version == "1.0.0"
        kernel.shutdown()
        assert kernel.running == False
        print("✓ Kernel works")
        return True
    except Exception as e:
        print(f"✗ Kernel failed: {e}")
        return False


def test_filesystem():
    """Test virtual file system"""
    print("\nTesting filesystem...")
    try:
        from filesystem import VirtualFileSystem
        fs = VirtualFileSystem()
        
        # Test directory operations
        assert fs.is_directory("/")
        assert fs.exists("/etc")
        assert fs.exists("/home")
        
        # Test file operations
        fs.write_file("/test.txt", "Hello DoubOS!")
        content = fs.read_file("/test.txt")
        assert content == "Hello DoubOS!"
        
        # Test mkdir
        fs.mkdir("/testdir")
        assert fs.is_directory("/testdir")
        
        # Test remove
        fs.remove("/test.txt")
        assert not fs.exists("/test.txt")
        
        print("✓ Filesystem works")
        return True
    except Exception as e:
        print(f"✗ Filesystem failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_users():
    """Test user management"""
    print("\nTesting user management...")
    try:
        from users import UserManager
        um = UserManager()
        
        # Test default users
        assert "root" in um.users
        assert "admin" in um.users
        assert "guest" in um.users
        
        # Test authentication
        user = um.authenticate("admin", "admin123")
        assert user is not None
        assert user.username == "admin"
        
        # Test failed auth
        user = um.authenticate("admin", "wrongpassword")
        assert user is None
        
        # Test login
        assert um.login("admin", "admin123") == True
        assert um.get_current_user().username == "admin"
        
        print("✓ User management works")
        return True
    except Exception as e:
        print(f"✗ User management failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_commands():
    """Test command processor"""
    print("\nTesting command processor...")
    try:
        from kernel import DoubOSKernel, DoubOSShell
        from filesystem import VirtualFileSystem
        from users import UserManager
        from commands import CommandProcessor, CommandContext
        
        kernel = DoubOSKernel()
        fs = VirtualFileSystem()
        um = UserManager()
        um.login("admin", "admin123")
        shell = DoubOSShell(kernel)
        
        context = CommandContext(kernel, fs, um, shell)
        processor = CommandProcessor(context)
        context.commands = processor.commands
        
        # Test basic commands
        output = processor.execute("pwd")
        assert output == "/"
        
        output = processor.execute("whoami")
        assert "admin" in output
        
        # Test file commands
        processor.execute("touch /test.txt")
        assert fs.exists("/test.txt")
        
        print("✓ Command processor works")
        return True
    except Exception as e:
        print(f"✗ Command processor failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dangerous_commands():
    """Test dangerous commands"""
    print("\nTesting dangerous commands...")
    try:
        from kernel import DoubOSKernel, DoubOSShell
        from filesystem import VirtualFileSystem
        from users import UserManager
        from commands import CommandProcessor, CommandContext
        from dangerous_commands import register_dangerous_commands
        
        kernel = DoubOSKernel()
        fs = VirtualFileSystem()
        um = UserManager()
        um.login("admin", "admin123")
        shell = DoubOSShell(kernel)
        
        context = CommandContext(kernel, fs, um, shell)
        processor = CommandProcessor(context)
        register_dangerous_commands(processor)
        context.commands = processor.commands
        
        # Test format command exists
        assert "format" in processor.commands
        assert "nuke" in processor.commands
        assert "shred" in processor.commands
        
        print("✓ Dangerous commands registered")
        return True
    except Exception as e:
        print(f"✗ Dangerous commands failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("DoubOS Test Suite")
    print("="*60)
    
    tests = [
        test_imports,
        test_kernel,
        test_filesystem,
        test_users,
        test_commands,
        test_dangerous_commands
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 All tests passed! DoubOS is ready to use!")
        print("\nRun: python doubos.py")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
