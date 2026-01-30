"""
DoubOS - Dangerous System Commands
WARNING: These commands simulate destructive operations!
"""

from commands import Command, CommandContext
from typing import List
import time


class FormatCommand(Command):
    """Format (wipe) the entire file system - EXTREMELY DANGEROUS!"""
    
    def __init__(self):
        super().__init__(
            "format",
            "⚠️  DANGER: Format and erase entire file system",
            "format --confirm",
            requires_admin=True
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if "--confirm" not in args:
            return """⚠️  ⚠️  ⚠️  DANGER ZONE ⚠️  ⚠️  ⚠️

This command will COMPLETELY ERASE the file system!
All files, directories, and data will be PERMANENTLY DELETED!

To proceed, run: format --confirm

Think carefully before doing this!"""
        
        # Perform the format
        output = ["\n" + "="*60]
        output.append("🔥 FORMATTING FILE SYSTEM 🔥")
        output.append("="*60)
        output.append("\n⏳ Erasing all data...")
        
        # Simulate formatting process
        stages = [
            "Unmounting file systems...",
            "Clearing superblock...",
            "Zeroing inode tables...",
            "Wiping data blocks...",
            "Removing directory entries...",
            "Clearing metadata..."
        ]
        
        result = "\n".join(output)
        for stage in stages:
            result += f"\n   [{stage}] ✓"
            
        # Actually format the file system
        context.filesystem.format()
        
        result += f"\n\n✅ File system formatted successfully!"
        result += f"\n⚠️  All data has been erased!"
        result += f"\n💡 Reinitializing default structure..."
        
        # Reinitialize basic structure
        context.filesystem.initialize_default_structure()
        
        result += f"\n✓  Basic structure restored\n"
        return result


class NukeCommand(Command):
    """Nuclear option - wipe EVERYTHING including users and system state"""
    
    def __init__(self):
        super().__init__(
            "nuke",
            "☢️  DANGER: Complete system wipe (filesystem + users + all state)",
            "nuke --i-am-absolutely-sure",
            requires_admin=True
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if "--i-am-absolutely-sure" not in args:
            return """☢️  ☢️  ☢️  NUCLEAR OPTION ☢️  ☢️  ☢️

This is the most destructive command in DoubOS!

This will PERMANENTLY DELETE:
  • Entire file system
  • All user accounts (except root)
  • Command history
  • Environment variables
  • System logs
  • EVERYTHING!

This action CANNOT be undone!

To proceed with total annihilation, run:
  nuke --i-am-absolutely-sure

⚠️  You have been warned! ⚠️"""
        
        output = ["\n" + "☢"*30]
        output.append("INITIATING NUCLEAR PROTOCOL")
        output.append("☢"*30)
        output.append("")
        
        # Countdown
        output.append("⏰ Countdown initiated...")
        countdown_text = "   "
        for i in range(5, 0, -1):
            countdown_text += f"{i}... "
        output.append(countdown_text + "💥")
        output.append("")
        
        # Nuke sequence
        output.append("🔥 NUKING ALL SYSTEMS:")
        output.append("   [Wiping file system...] ☢️")
        context.filesystem.format()
        
        output.append("   [Removing user accounts...] ☢️")
        # Remove all users except root
        users_to_remove = [u for u in context.user_manager.users.keys() if u != "root"]
        for username in users_to_remove:
            context.user_manager.remove_user(username)
            
        output.append("   [Clearing command history...] ☢️")
        context.kernel.command_history.clear()
        
        output.append("   [Resetting environment...] ☢️")
        context.kernel.environment_vars.clear()
        
        output.append("   [Destroying logs...] ☢️")
        output.append("   [Obliterating metadata...] ☢️")
        output.append("")
        output.append("💀 SYSTEM ANNIHILATED 💀")
        output.append("")
        output.append("Reinitializing minimal system...")
        
        # Reinitialize bare minimum
        context.filesystem.initialize_default_structure()
        context.user_manager.initialize_default_users()
        context.kernel.environment_vars = {
            "OS_NAME": "DoubOS",
            "OS_VERSION": "1.0.0"
        }
        
        output.append("✓  Minimal system restored")
        output.append("\n⚠️  All previous data has been permanently destroyed!")
        
        return "\n".join(output)


class ShredCommand(Command):
    """Securely delete a file by overwriting it multiple times"""
    
    def __init__(self):
        super().__init__(
            "shred",
            "Securely delete file (overwrite multiple times)",
            "shred <file>",
            requires_admin=False
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "shred: missing file operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        if not context.filesystem.is_file(target):
            return f"shred: {args[0]}: No such file"
            
        output = [f"🔒 Securely shredding: {args[0]}"]
        
        # Simulate shredding passes
        passes = 7
        for i in range(1, passes + 1):
            output.append(f"   Pass {i}/{passes}: Overwriting with random data... ✓")
            
        # Actually remove the file
        context.filesystem.remove(target)
        
        output.append(f"✓  File securely erased!")
        return "\n".join(output)


class WipeCommand(Command):
    """Wipe a directory and all its contents"""
    
    def __init__(self):
        super().__init__(
            "wipe",
            "Completely wipe a directory and all contents",
            "wipe <directory> --confirm",
            requires_admin=True
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "wipe: missing directory operand"
            
        # Remove --confirm from args
        confirm = "--confirm" in args
        args = [a for a in args if a != "--confirm"]
        
        if not args:
            return "wipe: missing directory operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        if target == "/":
            return "wipe: cannot wipe root directory (use 'format' instead)"
            
        if not context.filesystem.is_directory(target):
            return f"wipe: {args[0]}: Not a directory"
            
        if not confirm:
            file_count = len(context.filesystem.list_directory(target) or [])
            return f"""⚠️  WARNING: This will permanently delete:
   Directory: {args[0]}
   Contents: {file_count} items

To proceed, run: wipe {args[0]} --confirm"""
        
        # Count items before wiping
        items = context.filesystem.list_directory(target) or []
        count = len(items)
        
        # Wipe the directory
        if context.filesystem.remove(target, recursive=True):
            return f"✓  Wiped {args[0]} ({count} items deleted)"
        else:
            return f"wipe: failed to wipe {args[0]}"


class KillallCommand(Command):
    """Terminate all processes (simulated)"""
    
    def __init__(self):
        super().__init__(
            "killall",
            "Terminate all processes",
            "killall --confirm",
            requires_admin=True
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if "--confirm" not in args:
            return """⚠️  WARNING: This will terminate ALL processes!

To proceed, run: killall --confirm"""
        
        return """🔪 Terminating all processes...
   [Killing user processes...] ✓
   [Killing system daemons...] ✓
   [Stopping services...] ✓

✓  All processes terminated!
⚠️  System may be unstable"""


class CorruptCommand(Command):
    """Simulate data corruption (fills files with garbage)"""
    
    def __init__(self):
        super().__init__(
            "corrupt",
            "🎲 Simulate data corruption in a file",
            "corrupt <file>",
            requires_admin=True
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "corrupt: missing file operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        content = context.filesystem.read_file(target)
        if content is None:
            return f"corrupt: {args[0]}: No such file"
            
        # Create corrupted version
        import random
        corrupted = ''.join(random.choice('!@#$%^&*()~`{}[]|\\:;"<>,.?/') 
                           for _ in range(len(content)))
        
        user = context.user_manager.get_current_user()
        owner = user.username if user else "guest"
        context.filesystem.write_file(target, corrupted, owner)
        
        return f"⚠️  File corrupted: {args[0]}\n💀 Data is now unreadable!"


class ForkbombCommand(Command):
    """Simulate a fork bomb (process explosion)"""
    
    def __init__(self):
        super().__init__(
            "forkbomb",
            "💣 Simulate a fork bomb (process explosion)",
            "forkbomb",
            requires_admin=True
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return """💣 FORK BOMB TRIGGERED! 💣

Processes spawning exponentially:
   2 → 4 → 8 → 16 → 32 → 64 → 128 → 256 → 512 → 1024 → 2048 → 4096...

⚠️  System resources exhausted!
⚠️  System frozen!
⚠️  Requires hard reboot!

[In a real system, this would crash everything]
[Simulated for safety - your system is fine!]"""


class LogbombCommand(Command):
    """Fill logs with massive amounts of data"""
    
    def __init__(self):
        super().__init__(
            "logbomb",
            "📝 Fill system logs with massive data",
            "logbomb",
            requires_admin=True
        )
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        # Generate massive log entry
        log_entry = "[WARNING] " * 1000 + "\n"
        
        user = context.user_manager.get_current_user()
        owner = user.username if user else "guest"
        
        context.filesystem.write_file("/var/log/system.log", log_entry, owner, append=True)
        
        return f"""📝 LOG BOMB DEPLOYED!

   Wrote {len(log_entry)} bytes to system.log
   Log file is now {context.filesystem.get_size('/var/log/system.log')} bytes

⚠️  Disk space consumed!
⚠️  System logging impacted!"""


# Function to register all dangerous commands
def register_dangerous_commands(processor):
    """Register all dangerous commands with the processor"""
    processor.register_command(FormatCommand())
    processor.register_command(NukeCommand())
    processor.register_command(ShredCommand())
    processor.register_command(WipeCommand())
    processor.register_command(KillallCommand())
    processor.register_command(CorruptCommand())
    processor.register_command(ForkbombCommand())
    processor.register_command(LogbombCommand())
