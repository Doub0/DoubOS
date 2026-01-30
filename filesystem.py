"""
DoubOS - Virtual File System
Simulates a complete file system with files, directories, and permissions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


class FileNode:
    """Represents a file or directory in the file system"""
    
    def __init__(self, name: str, is_directory: bool = False, owner: str = "root", 
                 permissions: str = "rwxr-xr-x", content: str = ""):
        self.name = name
        self.is_directory = is_directory
        self.owner = owner
        self.permissions = permissions
        self.content = content
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.size = len(content) if not is_directory else 0
        self.children = {} if is_directory else None
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = {
            "name": self.name,
            "is_directory": self.is_directory,
            "owner": self.owner,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "size": self.size
        }
        if self.is_directory:
            data["children"] = {k: v.to_dict() for k, v in self.children.items()}
        else:
            data["content"] = self.content
        return data
        
    @staticmethod
    def from_dict(data: Dict) -> 'FileNode':
        """Create FileNode from dictionary"""
        node = FileNode(
            data["name"],
            data["is_directory"],
            data["owner"],
            data["permissions"],
            data.get("content", "")
        )
        node.created_at = datetime.fromisoformat(data["created_at"])
        node.modified_at = datetime.fromisoformat(data["modified_at"])
        node.size = data["size"]
        if data["is_directory"]:
            node.children = {k: FileNode.from_dict(v) for k, v in data["children"].items()}
        return node


class VirtualFileSystem:
    """Complete virtual file system implementation"""
    
    def __init__(self):
        self.root = FileNode("/", is_directory=True)
        self.initialize_default_structure()
        
    def initialize_default_structure(self):
        """Create default directory structure"""
        # Create standard Unix-like directories
        directories = [
            "/bin",      # Binary executables
            "/sbin",     # System binaries
            "/etc",      # Configuration files
            "/home",     # User home directories
            "/home/admin",
            "/home/guest",
            "/tmp",      # Temporary files
            "/var",      # Variable data
            "/var/log",  # Log files
            "/usr",      # User programs
            "/usr/bin",
            "/usr/local",
            "/dev",      # Device files
            "/proc",     # Process information
        ]
        
        for dir_path in directories:
            self.mkdir(dir_path, recursive=True)
            
        # Create some default files
        self.write_file("/etc/motd", "Welcome to DoubOS!\nA powerful operating system simulator.\n")
        self.write_file("/etc/hosts", "127.0.0.1 localhost\n")
        self.write_file("/home/admin/.profile", "# Admin profile\nexport PATH=/bin:/usr/bin:/sbin\n")
        self.write_file("/var/log/system.log", f"[{datetime.now()}] DoubOS initialized\n")
        
    def _get_node(self, path: str) -> Optional[FileNode]:
        """Get node at given path"""
        if path == "/":
            return self.root
            
        parts = [p for p in path.split("/") if p]
        current = self.root
        
        for part in parts:
            if not current.is_directory or part not in current.children:
                return None
            current = current.children[part]
            
        return current
        
    def _get_parent_and_name(self, path: str) -> tuple[Optional[FileNode], str]:
        """Get parent node and filename from path"""
        if path == "/":
            return None, "/"
            
        parts = [p for p in path.split("/") if p]
        parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
        parent = self._get_node(parent_path)
        return parent, parts[-1]
        
    def exists(self, path: str) -> bool:
        """Check if path exists"""
        return self._get_node(path) is not None
        
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory"""
        node = self._get_node(path)
        return node is not None and node.is_directory
        
    def is_file(self, path: str) -> bool:
        """Check if path is a file"""
        node = self._get_node(path)
        return node is not None and not node.is_directory
        
    def mkdir(self, path: str, recursive: bool = False, owner: str = "root") -> bool:
        """Create directory"""
        if self.exists(path):
            return False
            
        parent, name = self._get_parent_and_name(path)
        
        if parent is None:
            if recursive and path != "/":
                # Create parent directories
                parts = [p for p in path.split("/") if p]
                current_path = ""
                for part in parts:
                    current_path += "/" + part
                    if not self.exists(current_path):
                        parent_node, dir_name = self._get_parent_and_name(current_path)
                        if parent_node and parent_node.is_directory:
                            parent_node.children[dir_name] = FileNode(dir_name, True, owner)
                return True
            return False
            
        if not parent.is_directory:
            return False
            
        parent.children[name] = FileNode(name, is_directory=True, owner=owner)
        return True
        
    def write_file(self, path: str, content: str, owner: str = "root", append: bool = False) -> bool:
        """Write content to file"""
        parent, name = self._get_parent_and_name(path)
        
        if parent is None or not parent.is_directory:
            return False
            
        if name in parent.children:
            # File exists, update it
            node = parent.children[name]
            if node.is_directory:
                return False
            if append:
                node.content += content
            else:
                node.content = content
            node.size = len(node.content)
            node.modified_at = datetime.now()
        else:
            # Create new file
            parent.children[name] = FileNode(name, is_directory=False, owner=owner, content=content)
            
        return True
        
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        node = self._get_node(path)
        if node and not node.is_directory:
            return node.content
        return None
        
    def list_directory(self, path: str) -> Optional[List[FileNode]]:
        """List directory contents"""
        node = self._get_node(path)
        if node and node.is_directory:
            return list(node.children.values())
        return None
        
    def remove(self, path: str, recursive: bool = False) -> bool:
        """Remove file or directory"""
        if path == "/":
            return False  # Can't remove root
            
        parent, name = self._get_parent_and_name(path)
        
        if parent is None or name not in parent.children:
            return False
            
        node = parent.children[name]
        
        if node.is_directory and node.children and not recursive:
            return False  # Directory not empty
            
        del parent.children[name]
        return True
        
    def move(self, src: str, dst: str) -> bool:
        """Move/rename file or directory"""
        src_parent, src_name = self._get_parent_and_name(src)
        dst_parent, dst_name = self._get_parent_and_name(dst)
        
        if not src_parent or src_name not in src_parent.children:
            return False
            
        if not dst_parent or not dst_parent.is_directory:
            return False
            
        node = src_parent.children[src_name]
        node.name = dst_name
        dst_parent.children[dst_name] = node
        del src_parent.children[src_name]
        return True
        
    def copy(self, src: str, dst: str) -> bool:
        """Copy file or directory"""
        src_node = self._get_node(src)
        if not src_node:
            return False
            
        dst_parent, dst_name = self._get_parent_and_name(dst)
        if not dst_parent or not dst_parent.is_directory:
            return False
            
        # Deep copy the node
        import copy
        new_node = copy.deepcopy(src_node)
        new_node.name = dst_name
        dst_parent.children[dst_name] = new_node
        return True
        
    def get_size(self, path: str) -> int:
        """Get size of file or directory"""
        node = self._get_node(path)
        if not node:
            return 0
            
        if not node.is_directory:
            return node.size
            
        # Recursively calculate directory size
        total = 0
        for child in node.children.values():
            if child.is_directory:
                child_path = path.rstrip("/") + "/" + child.name
                total += self.get_size(child_path)
            else:
                total += child.size
        return total
        
    def format(self):
        """Format (clear) the entire file system - DANGEROUS!"""
        self.root = FileNode("/", is_directory=True)
        
    def save_to_disk(self, filepath: str):
        """Save file system to disk"""
        with open(filepath, 'w') as f:
            json.dump(self.root.to_dict(), f, indent=2)
            
    def load_from_disk(self, filepath: str):
        """Load file system from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.root = FileNode.from_dict(data)
