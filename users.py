"""
DoubOS - User Management System
Handles user authentication, permissions, and sessions
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class User:
    """Represents a system user"""
    
    def __init__(self, username: str, password_hash: str, uid: int, 
                 home_dir: str = None, is_admin: bool = False):
        self.username = username
        self.password_hash = password_hash
        self.uid = uid
        self.home_dir = home_dir or f"/home/{username}"
        self.is_admin = is_admin
        self.created_at = datetime.now()
        self.last_login = None
        self.login_count = 0
        
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
        
    def update_password(self, new_password: str):
        """Update user password"""
        self.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "uid": self.uid,
            "home_dir": self.home_dir,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count
        }
        
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """Create User from dictionary"""
        user = User(
            data["username"],
            data["password_hash"],
            data["uid"],
            data["home_dir"],
            data["is_admin"]
        )
        user.created_at = datetime.fromisoformat(data["created_at"])
        if data["last_login"]:
            user.last_login = datetime.fromisoformat(data["last_login"])
        user.login_count = data["login_count"]
        return user


class UserManager:
    """Manages system users and authentication"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.next_uid = 1000
        self.current_session = None
        self.initialize_default_users()
        
    def initialize_default_users(self):
        """Create default system users"""
        # Root user (admin)
        self.add_user("root", "root123", is_admin=True)
        self.users["root"].uid = 0
        
        # Admin user
        self.add_user("admin", "admin123", is_admin=True)
        
        # Guest user
        self.add_user("guest", "guest", is_admin=False)
        
    def add_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """Add a new user"""
        if username in self.users:
            return False
            
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(username, password_hash, self.next_uid, is_admin=is_admin)
        self.users[username] = user
        self.next_uid += 1
        return True
        
    def remove_user(self, username: str) -> bool:
        """Remove a user"""
        if username == "root" or username not in self.users:
            return False
        del self.users[username]
        return True
        
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with password"""
        user = self.users.get(username)
        if user and user.verify_password(password):
            user.last_login = datetime.now()
            user.login_count += 1
            return user
        return None
        
    def login(self, username: str, password: str) -> bool:
        """Login user"""
        user = self.authenticate(username, password)
        if user:
            self.current_session = user
            return True
        return False
        
    def logout(self):
        """Logout current user"""
        self.current_session = None
        
    def get_current_user(self) -> Optional[User]:
        """Get currently logged in user"""
        return self.current_session
        
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.current_session and self.current_session.is_admin
        
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.users.get(username)
        if user and user.verify_password(old_password):
            user.update_password(new_password)
            return True
        return False
        
    def list_users(self) -> List[User]:
        """List all users"""
        return list(self.users.values())
        
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)
        
    def save_to_disk(self, filepath: str):
        """Save users to disk"""
        data = {username: user.to_dict() for username, user in self.users.items()}
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load_from_disk(self, filepath: str):
        """Load users from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.users = {username: User.from_dict(user_data) 
                             for username, user_data in data.items()}
                # Update next_uid
                if self.users:
                    self.next_uid = max(user.uid for user in self.users.values()) + 1
