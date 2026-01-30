"""
DoubOS - Command Processor
Handles command parsing and execution
"""

from typing import Dict, Callable, List, Optional
from datetime import datetime
import os
import shutil


class Command:
    """Base class for commands"""
    
    def __init__(self, name: str, description: str, usage: str, 
                 requires_admin: bool = False):
        self.name = name
        self.description = description
        self.usage = usage
        self.requires_admin = requires_admin
        
    def execute(self, args: List[str], context: 'CommandContext') -> str:
        """Execute the command"""
        raise NotImplementedError


class CommandContext:
    """Context for command execution"""
    
    def __init__(self, kernel, filesystem, user_manager, shell):
        self.kernel = kernel
        self.filesystem = filesystem
        self.user_manager = user_manager
        self.shell = shell
        self.current_dir = "/"


class CommandProcessor:
    """Processes and executes commands"""
    
    def __init__(self, context: CommandContext):
        self.context = context
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {
            "ll": "ls -l",
            "la": "ls -a",
            "..": "cd ..",
            "cls": "clear",
            "dir": "ls"
        }
        self.register_builtin_commands()
        
    def register_command(self, command: Command):
        """Register a command"""
        self.commands[command.name] = command
        
    def execute(self, command_line: str) -> Optional[str]:
        """Execute a command line"""
        # Handle empty command
        if not command_line.strip():
            return None
            
        # Expand aliases
        for alias, expansion in self.aliases.items():
            if command_line.startswith(alias + " ") or command_line == alias:
                command_line = command_line.replace(alias, expansion, 1)
                
        # Parse command and arguments
        parts = command_line.split()
        cmd_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Find command
        command = self.commands.get(cmd_name)
        if not command:
            return f"⚠️  Command not found: {cmd_name}\nType 'help' for available commands."
            
        # Check admin privileges
        if command.requires_admin and not self.context.user_manager.is_admin():
            return f"❌ Permission denied: {cmd_name} requires administrator privileges"
            
        # Execute command
        try:
            return command.execute(args, self.context)
        except Exception as e:
            return f"❌ Error executing {cmd_name}: {str(e)}"
            
    def register_builtin_commands(self):
        """Register all built-in commands"""
        # Navigation commands
        self.register_command(CdCommand())
        self.register_command(PwdCommand())
        self.register_command(LsCommand())
        
        # File operations
        self.register_command(CatCommand())
        self.register_command(TouchCommand())
        self.register_command(MkdirCommand())
        self.register_command(RmCommand())
        self.register_command(CpCommand())
        self.register_command(MvCommand())
        self.register_command(EchoCommand())
        
        # System commands
        self.register_command(ClearCommand())
        self.register_command(DateCommand())
        self.register_command(UptimeCommand())
        self.register_command(WhoamiCommand())
        self.register_command(UnameCommand())
        self.register_command(HistoryCommand())
        self.register_command(EnvCommand())
        
        # User commands
        self.register_command(PasswdCommand())
        self.register_command(SuCommand())
        self.register_command(UsersCommand())
        
        # System info
        self.register_command(DfCommand())
        self.register_command(PsCommand())
        self.register_command(TopCommand())
        
        # Utility commands
        self.register_command(HelpCommand())
        self.register_command(ManCommand())
        self.register_command(AliasCommand())
        
        # Power commands
        self.register_command(ShutdownCommand())
        self.register_command(RebootCommand())
        self.register_command(ExitCommand())


# ============= NAVIGATION COMMANDS =============

class CdCommand(Command):
    def __init__(self):
        super().__init__("cd", "Change directory", "cd <directory>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            # Go to home directory
            user = context.user_manager.get_current_user()
            target = user.home_dir if user else "/home"
        elif args[0] == "..":
            # Go to parent directory
            parts = context.current_dir.split("/")
            target = "/".join(parts[:-1]) or "/"
        elif args[0].startswith("/"):
            # Absolute path
            target = args[0]
        else:
            # Relative path
            target = context.current_dir.rstrip("/") + "/" + args[0]
            
        # Normalize path
        target = target.replace("//", "/")
        
        if context.filesystem.is_directory(target):
            context.current_dir = target
            context.shell.change_directory(target)
            return None
        else:
            return f"cd: {args[0]}: No such directory"


class PwdCommand(Command):
    def __init__(self):
        super().__init__("pwd", "Print working directory", "pwd")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return context.current_dir


class LsCommand(Command):
    def __init__(self):
        super().__init__("ls", "List directory contents", "ls [-l] [-a] [directory]")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        long_format = "-l" in args
        show_hidden = "-a" in args
        
        # Remove flags from args
        args = [a for a in args if not a.startswith("-")]
        
        # Determine target directory
        target = args[0] if args else context.current_dir
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        # List directory
        items = context.filesystem.list_directory(target)
        if items is None:
            return f"ls: cannot access '{target}': No such file or directory"
            
        # Filter hidden files
        if not show_hidden:
            items = [item for item in items if not item.name.startswith(".")]
            
        if not items:
            return ""
            
        # Format output
        if long_format:
            lines = []
            for item in sorted(items, key=lambda x: x.name):
                item_type = "d" if item.is_directory else "-"
                size = item.size
                date = item.modified_at.strftime("%b %d %H:%M")
                color = "\033[94m" if item.is_directory else "\033[0m"
                reset = "\033[0m"
                lines.append(f"{item_type}{item.permissions} {item.owner:8} {size:8} {date} {color}{item.name}{reset}")
            return "\n".join(lines)
        else:
            # Simple format with colors
            result = []
            for item in sorted(items, key=lambda x: x.name):
                if item.is_directory:
                    result.append(f"\033[94m{item.name}/\033[0m")
                else:
                    result.append(item.name)
            return "  ".join(result)


# ============= FILE OPERATIONS =============

class CatCommand(Command):
    def __init__(self):
        super().__init__("cat", "Display file contents", "cat <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "cat: missing file operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        content = context.filesystem.read_file(target)
        if content is None:
            return f"cat: {args[0]}: No such file or directory"
        return content.rstrip()


class TouchCommand(Command):
    def __init__(self):
        super().__init__("touch", "Create empty file or update timestamp", "touch <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "touch: missing file operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        user = context.user_manager.get_current_user()
        owner = user.username if user else "guest"
        
        if context.filesystem.write_file(target, "", owner):
            return None
        else:
            return f"touch: cannot create '{args[0]}'"


class MkdirCommand(Command):
    def __init__(self):
        super().__init__("mkdir", "Create directory", "mkdir [-p] <directory>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "mkdir: missing operand"
            
        recursive = "-p" in args
        args = [a for a in args if not a.startswith("-")]
        
        if not args:
            return "mkdir: missing operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        user = context.user_manager.get_current_user()
        owner = user.username if user else "guest"
        
        if context.filesystem.mkdir(target, recursive, owner):
            return None
        else:
            return f"mkdir: cannot create directory '{args[0]}'"


class RmCommand(Command):
    def __init__(self):
        super().__init__("rm", "Remove files or directories", "rm [-r] <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "rm: missing operand"
            
        recursive = "-r" in args or "-rf" in args
        force = "-f" in args or "-rf" in args
        args = [a for a in args if not a.startswith("-")]
        
        if not args:
            return "rm: missing operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        if context.filesystem.remove(target, recursive):
            return None
        else:
            if not force:
                return f"rm: cannot remove '{args[0]}'"
            return None


class CpCommand(Command):
    def __init__(self):
        super().__init__("cp", "Copy files", "cp <source> <destination>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if len(args) < 2:
            return "cp: missing destination file operand"
            
        src = args[0]
        dst = args[1]
        
        if not src.startswith("/"):
            src = context.current_dir.rstrip("/") + "/" + src
        if not dst.startswith("/"):
            dst = context.current_dir.rstrip("/") + "/" + dst
            
        if context.filesystem.copy(src, dst):
            return None
        else:
            return f"cp: cannot copy '{args[0]}' to '{args[1]}'"


class MvCommand(Command):
    def __init__(self):
        super().__init__("mv", "Move/rename files", "mv <source> <destination>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if len(args) < 2:
            return "mv: missing destination file operand"
            
        src = args[0]
        dst = args[1]
        
        if not src.startswith("/"):
            src = context.current_dir.rstrip("/") + "/" + src
        if not dst.startswith("/"):
            dst = context.current_dir.rstrip("/") + "/" + dst
            
        if context.filesystem.move(src, dst):
            return None
        else:
            return f"mv: cannot move '{args[0]}' to '{args[1]}'"


class EchoCommand(Command):
    def __init__(self):
        super().__init__("echo", "Display a line of text", "echo <text>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return " ".join(args)


# ============= SYSTEM COMMANDS =============

class ClearCommand(Command):
    def __init__(self):
        super().__init__("clear", "Clear the screen", "clear")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        os.system('cls' if os.name == 'nt' else 'clear')
        return None


class DateCommand(Command):
    def __init__(self):
        super().__init__("date", "Display current date and time", "date")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")


class UptimeCommand(Command):
    def __init__(self):
        super().__init__("uptime", "Show system uptime", "uptime")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        uptime = context.kernel.get_uptime()
        return f"System uptime: {uptime}"


class WhoamiCommand(Command):
    def __init__(self):
        super().__init__("whoami", "Display current user", "whoami")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        user = context.user_manager.get_current_user()
        return user.username if user else "guest"


class UnameCommand(Command):
    def __init__(self):
        super().__init__("uname", "Display system information", "uname [-a]")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if "-a" in args:
            return f"DoubOS {context.kernel.version} (Virtual OS Simulator)"
        return "DoubOS"


class HistoryCommand(Command):
    def __init__(self):
        super().__init__("history", "Display command history", "history")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        history = context.kernel.command_history
        if not history:
            return ""
        lines = []
        for i, entry in enumerate(history[-50:], 1):  # Last 50 commands
            lines.append(f"{i:4d}  {entry['command']}")
        return "\n".join(lines)


class EnvCommand(Command):
    def __init__(self):
        super().__init__("env", "Display environment variables", "env")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        lines = []
        for key, value in context.kernel.environment_vars.items():
            lines.append(f"{key}={value}")
        return "\n".join(lines)


# ============= USER COMMANDS =============

class PasswdCommand(Command):
    def __init__(self):
        super().__init__("passwd", "Change user password", "passwd")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return "Password change requires interactive mode (not available in simulation)"


class SuCommand(Command):
    def __init__(self):
        super().__init__("su", "Switch user", "su [username]")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return "User switching requires interactive mode (not available in simulation)"


class UsersCommand(Command):
    def __init__(self):
        super().__init__("users", "List all users", "users")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        users = context.user_manager.list_users()
        lines = []
        for user in sorted(users, key=lambda u: u.uid):
            admin_badge = "👑 " if user.is_admin else "   "
            lines.append(f"{admin_badge}{user.username:15} UID: {user.uid:4} Home: {user.home_dir}")
        return "\n".join(lines)


# ============= SYSTEM INFO =============

class DfCommand(Command):
    def __init__(self):
        super().__init__("df", "Display disk space usage", "df")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        total_size = context.filesystem.get_size("/")
        return f"Filesystem     Size    Used\n/             Virtual  {total_size}B"


class PsCommand(Command):
    def __init__(self):
        super().__init__("ps", "List running processes", "ps")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        user = context.user_manager.get_current_user()
        username = user.username if user else "guest"
        return f"PID  USER      COMMAND\n  1  root      init\n  2  {username:8}  shell"


class TopCommand(Command):
    def __init__(self):
        super().__init__("top", "Display system resource usage", "top")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        uptime = context.kernel.get_uptime()
        user = context.user_manager.get_current_user()
        username = user.username if user else "guest"
        return f"""DoubOS System Monitor
Uptime: {uptime}
User: {username}
Processes: 2 total
Memory: Virtual (unlimited)"""


# ============= UTILITY COMMANDS =============

class HelpCommand(Command):
    def __init__(self):
        super().__init__("help", "Display help information", "help [command]")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if args:
            # Help for specific command
            cmd_name = args[0]
            cmd = context.commands.get(cmd_name)
            if cmd:
                admin_flag = " [ADMIN]" if cmd.requires_admin else ""
                return f"{cmd.name}{admin_flag} - {cmd.description}\nUsage: {cmd.usage}"
            else:
                return f"No help available for: {cmd_name}"
        
        # General help
        categories = {
            "Navigation": ["cd", "pwd", "ls"],
            "File Operations": ["cat", "touch", "mkdir", "rm", "cp", "mv", "echo"],
            "System": ["clear", "date", "uptime", "whoami", "uname", "history", "env"],
            "Users": ["passwd", "su", "users"],
            "Info": ["df", "ps", "top"],
            "Power": ["shutdown", "reboot", "exit"],
            "Dangerous": ["format", "nuke"],
            "Help": ["help", "man"]
        }
        
        output = ["DoubOS Available Commands\n"]
        for category, commands in categories.items():
            output.append(f"\n{category}:")
            for cmd_name in commands:
                cmd = context.commands.get(cmd_name)
                if cmd:
                    admin_flag = "🔒" if cmd.requires_admin else "  "
                    output.append(f"  {admin_flag} {cmd.name:12} - {cmd.description}")
        
        output.append("\n\nType 'help <command>' for detailed information")
        output.append("🔒 = Requires admin privileges")
        return "\n".join(output)


class ManCommand(Command):
    def __init__(self):
        super().__init__("man", "Display manual pages", "man <command>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "What manual page do you want?"
        return HelpCommand().execute(args, context)


class AliasCommand(Command):
    def __init__(self):
        super().__init__("alias", "Display command aliases", "alias")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        # This would need access to processor.aliases
        return "ll='ls -l'\nla='ls -a'\n..='cd ..'\ncls='clear'\ndir='ls'"


# ============= POWER COMMANDS =============

class ShutdownCommand(Command):
    def __init__(self):
        super().__init__("shutdown", "Shutdown the system", "shutdown", requires_admin=False)
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        context.kernel.shutdown()
        return None


class RebootCommand(Command):
    def __init__(self):
        super().__init__("reboot", "Reboot the system", "reboot", requires_admin=True)
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return "⚠️  Reboot would restart DoubOS (not implemented in simulation)"


class ExitCommand(Command):
    def __init__(self):
        super().__init__("exit", "Exit the shell", "exit")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        context.kernel.shutdown()
        return None
