"""
DoubOS - Advanced Features and Utilities
Network simulation, package manager, and more
"""

from commands import Command, CommandContext
from typing import List
import random
from datetime import datetime


class PingCommand(Command):
    """Simulate network ping"""
    
    def __init__(self):
        super().__init__("ping", "Ping a host", "ping <host>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "ping: missing host operand"
            
        host = args[0]
        output = [f"PING {host} (192.168.1.{random.randint(1, 255)}): 56 data bytes"]
        
        for i in range(4):
            ms = random.uniform(1.5, 50.0)
            output.append(f"64 bytes from {host}: icmp_seq={i} ttl=64 time={ms:.1f} ms")
            
        output.append(f"\n--- {host} ping statistics ---")
        output.append(f"4 packets transmitted, 4 received, 0% packet loss")
        
        return "\n".join(output)


class WgetCommand(Command):
    """Simulate file download"""
    
    def __init__(self):
        super().__init__("wget", "Download file from URL", "wget <url>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "wget: missing URL"
            
        url = args[0]
        filename = url.split("/")[-1] or "index.html"
        
        output = [f"--{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}--  {url}"]
        output.append(f"Resolving host... {random.randint(100, 999)} ms")
        output.append(f"Connecting to host... connected.")
        output.append(f"HTTP request sent, awaiting response... 200 OK")
        
        size = random.randint(1024, 1024*1024)
        output.append(f"Length: {size} ({size/1024:.1f}K)")
        output.append(f"Saving to: '{filename}'")
        output.append("")
        output.append(f"100%[=======================================>] {size:,} bytes")
        output.append(f"\n'{filename}' saved [{size}/{size}]")
        
        # Actually create the file
        content = f"Downloaded from {url}\nSize: {size} bytes\n"
        user = context.user_manager.get_current_user()
        owner = user.username if user else "guest"
        target = context.current_dir.rstrip("/") + "/" + filename
        context.filesystem.write_file(target, content, owner)
        
        return "\n".join(output)


class CurlCommand(Command):
    """Fetch URL content"""
    
    def __init__(self):
        super().__init__("curl", "Transfer data from URL", "curl <url>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "curl: no URL specified"
            
        url = args[0]
        return f"""<!DOCTYPE html>
<html>
<head><title>Simulated Response</title></head>
<body>
<h1>DoubOS Network Simulation</h1>
<p>Requested URL: {url}</p>
<p>This is a simulated HTTP response.</p>
</body>
</html>"""


class IfconfigCommand(Command):
    """Display network interface configuration"""
    
    def __init__(self):
        super().__init__("ifconfig", "Display network interfaces", "ifconfig")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return """eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.{random.randint(10, 250)}  netmask 255.255.255.0  broadcast 192.168.1.255
        ether {random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}  txqueuelen 1000
        RX packets 1024  bytes 131072 (128.0 KB)
        TX packets 768   bytes 98304 (96.0 KB)

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000
        RX packets 256  bytes 32768 (32.0 KB)
        TX packets 256  bytes 32768 (32.0 KB)""".format(random=random)


class AptCommand(Command):
    """Package manager simulation"""
    
    def __init__(self):
        super().__init__("apt", "Package manager", "apt install <package>", requires_admin=True)
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args or args[0] not in ["install", "update", "upgrade", "remove"]:
            return "Usage: apt [install|update|upgrade|remove] <package>"
            
        action = args[0]
        
        if action == "update":
            return """Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
All packages are up to date."""
            
        if action == "upgrade":
            return """Reading package lists... Done
Building dependency tree... Done
Calculating upgrade... Done
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded."""
            
        if len(args) < 2:
            return f"apt {action}: missing package name"
            
        package = args[1]
        
        if action == "install":
            return f"""Reading package lists... Done
Building dependency tree... Done
The following NEW packages will be installed:
  {package}
0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
Need to get 0 B/{random.randint(100, 9999)} kB of archives.
After this operation, {random.randint(1024, 10240)} kB of additional disk space will be used.
Selecting previously unselected package {package}.
Unpacking {package} ...
Setting up {package} ...
✓  {package} installed successfully!"""
            
        if action == "remove":
            return f"""Reading package lists... Done
Building dependency tree... Done
The following packages will be REMOVED:
  {package}
0 upgraded, 0 newly installed, 1 to remove and 0 not upgraded.
After this operation, {random.randint(1024, 10240)} kB disk space will be freed.
Removing {package} ...
✓  {package} removed successfully!"""


class GrepCommand(Command):
    """Search for patterns in files"""
    
    def __init__(self):
        super().__init__("grep", "Search for pattern in file", "grep <pattern> <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if len(args) < 2:
            return "grep: missing pattern or file"
            
        pattern = args[0]
        target = args[1]
        
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        content = context.filesystem.read_file(target)
        if content is None:
            return f"grep: {args[1]}: No such file"
            
        # Simple pattern matching
        lines = content.split("\n")
        matches = [line for line in lines if pattern.lower() in line.lower()]
        
        if not matches:
            return ""
            
        # Highlight matches
        result = []
        for line in matches:
            highlighted = line.replace(pattern, f"\033[91m{pattern}\033[0m")
            result.append(highlighted)
            
        return "\n".join(result)


class FindCommand(Command):
    """Find files in directory hierarchy"""
    
    def __init__(self):
        super().__init__("find", "Search for files", "find <path> -name <pattern>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "find: missing path"
            
        path = args[0]
        if not path.startswith("/"):
            path = context.current_dir.rstrip("/") + "/" + path
            
        # Simple implementation - just list all files recursively
        def find_recursive(node_path, results):
            node = context.filesystem._get_node(node_path)
            if node and node.is_directory:
                for child_name, child in node.children.items():
                    child_path = node_path.rstrip("/") + "/" + child_name
                    results.append(child_path)
                    if child.is_directory:
                        find_recursive(child_path, results)
                        
        results = []
        find_recursive(path, results)
        
        # Filter by pattern if provided
        if "-name" in args:
            try:
                idx = args.index("-name")
                if idx + 1 < len(args):
                    pattern = args[idx + 1]
                    results = [r for r in results if pattern in r]
            except:
                pass
                
        return "\n".join(results) if results else ""


class TarCommand(Command):
    """Archive files"""
    
    def __init__(self):
        super().__init__("tar", "Archive utility", "tar -czf <archive.tar.gz> <files>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if len(args) < 3:
            return "tar: missing arguments\nUsage: tar -czf archive.tar.gz file1 file2 ..."
            
        if args[0] not in ["-czf", "-xzf"]:
            return "tar: invalid option (use -czf to create or -xzf to extract)"
            
        archive_name = args[1]
        
        if args[0] == "-czf":
            # Create archive
            files = args[2:]
            return f"""tar: Creating archive '{archive_name}'
tar: Adding {len(files)} file(s)...
tar: {archive_name} created successfully ({random.randint(1024, 102400)} bytes)"""
        else:
            # Extract archive
            return f"""tar: Extracting '{archive_name}'...
tar: Extracted {random.randint(1, 10)} file(s)
tar: Done"""


class ChmodCommand(Command):
    """Change file permissions"""
    
    def __init__(self):
        super().__init__("chmod", "Change file permissions", "chmod <mode> <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if len(args) < 2:
            return "chmod: missing operand"
            
        mode = args[0]
        target = args[1]
        
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        node = context.filesystem._get_node(target)
        if node:
            # Simulated - just acknowledge
            return None
        else:
            return f"chmod: cannot access '{args[1]}': No such file or directory"


class ChownCommand(Command):
    """Change file owner"""
    
    def __init__(self):
        super().__init__("chown", "Change file owner", "chown <owner> <file>", requires_admin=True)
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if len(args) < 2:
            return "chown: missing operand"
            
        owner = args[0]
        target = args[1]
        
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        node = context.filesystem._get_node(target)
        if node:
            node.owner = owner
            return None
        else:
            return f"chown: cannot access '{args[1]}': No such file or directory"


class TailCommand(Command):
    """Display last lines of file"""
    
    def __init__(self):
        super().__init__("tail", "Output last part of file", "tail [-n N] <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "tail: missing file operand"
            
        num_lines = 10
        file_arg = args[-1]
        
        if "-n" in args:
            try:
                idx = args.index("-n")
                num_lines = int(args[idx + 1])
                file_arg = args[-1]
            except:
                pass
                
        target = file_arg
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        content = context.filesystem.read_file(target)
        if content is None:
            return f"tail: {file_arg}: No such file"
            
        lines = content.split("\n")
        return "\n".join(lines[-num_lines:])


class HeadCommand(Command):
    """Display first lines of file"""
    
    def __init__(self):
        super().__init__("head", "Output first part of file", "head [-n N] <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "head: missing file operand"
            
        num_lines = 10
        file_arg = args[-1]
        
        if "-n" in args:
            try:
                idx = args.index("-n")
                num_lines = int(args[idx + 1])
            except:
                pass
                
        target = file_arg
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        content = context.filesystem.read_file(target)
        if content is None:
            return f"head: {file_arg}: No such file"
            
        lines = content.split("\n")
        return "\n".join(lines[:num_lines])


class WcCommand(Command):
    """Count lines, words, and characters"""
    
    def __init__(self):
        super().__init__("wc", "Word, line, and byte count", "wc <file>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        if not args:
            return "wc: missing file operand"
            
        target = args[0]
        if not target.startswith("/"):
            target = context.current_dir.rstrip("/") + "/" + target
            
        content = context.filesystem.read_file(target)
        if content is None:
            return f"wc: {args[0]}: No such file"
            
        lines = len(content.split("\n"))
        words = len(content.split())
        chars = len(content)
        
        return f"{lines:8} {words:8} {chars:8} {args[0]}"


# Function to register all utility commands
def register_utility_commands(processor):
    """Register all utility commands with the processor"""
    processor.register_command(PingCommand())
    processor.register_command(WgetCommand())
    processor.register_command(CurlCommand())
    processor.register_command(IfconfigCommand())
    processor.register_command(AptCommand())
    processor.register_command(GrepCommand())
    processor.register_command(FindCommand())
    processor.register_command(TarCommand())
    processor.register_command(ChmodCommand())
    processor.register_command(ChownCommand())
    processor.register_command(TailCommand())
    processor.register_command(HeadCommand())
    processor.register_command(WcCommand())
