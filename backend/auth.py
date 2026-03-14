"""Authentication system with JWT tokens."""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
import jwt

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# User storage file
USERS_FILE = Path(__file__).parent.parent / "users.json"


@dataclass
class User:
    username: str
    password_hash: str
    created_at: str
    is_active: bool = True
    display_name: Optional[str] = None


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = "ofc_solver_ai_salt_2024"  # In production, use unique salt per user
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == password_hash


def load_users() -> dict[str, User]:
    """Load users from JSON file."""
    if not USERS_FILE.exists():
        return {}
    
    try:
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
        return {username: User(**user_data) for username, user_data in data.items()}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}


def save_users(users: dict[str, User]):
    """Save users to JSON file."""
    data = {username: asdict(user) for username, user in users.items()}
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def create_user(username: str, password: str, display_name: str = None) -> User:
    """Create a new user."""
    users = load_users()
    
    if username in users:
        raise ValueError(f"User '{username}' already exists")
    
    user = User(
        username=username,
        password_hash=hash_password(password),
        created_at=datetime.now().isoformat(),
        is_active=True,
        display_name=display_name or username
    )
    
    users[username] = user
    save_users(users)
    
    return user


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    users = load_users()
    
    user = users.get(username)
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def create_access_token(username: str, expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the username."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return username
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user(username: str) -> Optional[User]:
    """Get a user by username."""
    users = load_users()
    return users.get(username)


def list_users() -> list[dict]:
    """List all users (without password hashes)."""
    users = load_users()
    return [
        {
            "username": u.username,
            "display_name": u.display_name,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users.values()
    ]


def update_user_password(username: str, new_password: str) -> bool:
    """Update a user's password."""
    users = load_users()
    
    if username not in users:
        return False
    
    users[username].password_hash = hash_password(new_password)
    save_users(users)
    return True


def deactivate_user(username: str) -> bool:
    """Deactivate a user."""
    users = load_users()
    
    if username not in users:
        return False
    
    users[username].is_active = False
    save_users(users)
    return True


def activate_user(username: str) -> bool:
    """Activate a user."""
    users = load_users()
    
    if username not in users:
        return False
    
    users[username].is_active = True
    save_users(users)
    return True


def delete_user(username: str) -> bool:
    """Delete a user."""
    users = load_users()
    
    if username not in users:
        return False
    
    del users[username]
    save_users(users)
    return True


# CLI for user management
if __name__ == "__main__":
    import sys
    
    def print_usage():
        print("""
User Management CLI

Usage:
    python auth.py create <username> <password> [display_name]
    python auth.py list
    python auth.py delete <username>
    python auth.py passwd <username> <new_password>
    python auth.py activate <username>
    python auth.py deactivate <username>
""")
    
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 4:
            print("Usage: python auth.py create <username> <password> [display_name]")
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3]
        display_name = sys.argv[4] if len(sys.argv) > 4 else None
        try:
            user = create_user(username, password, display_name)
            print(f"✅ Created user: {user.username}")
        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif command == "list":
        users = list_users()
        if users:
            print("Users:")
            for u in users:
                status = "✅" if u["is_active"] else "❌"
                print(f"  {status} {u['username']} ({u['display_name']})")
        else:
            print("No users found.")
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python auth.py delete <username>")
            sys.exit(1)
        username = sys.argv[2]
        if delete_user(username):
            print(f"✅ Deleted user: {username}")
        else:
            print(f"❌ User not found: {username}")
    
    elif command == "passwd":
        if len(sys.argv) < 4:
            print("Usage: python auth.py passwd <username> <new_password>")
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3]
        if update_user_password(username, password):
            print(f"✅ Password updated for: {username}")
        else:
            print(f"❌ User not found: {username}")
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("Usage: python auth.py activate <username>")
            sys.exit(1)
        username = sys.argv[2]
        if activate_user(username):
            print(f"✅ Activated user: {username}")
        else:
            print(f"❌ User not found: {username}")
    
    elif command == "deactivate":
        if len(sys.argv) < 3:
            print("Usage: python auth.py deactivate <username>")
            sys.exit(1)
        username = sys.argv[2]
        if deactivate_user(username):
            print(f"✅ Deactivated user: {username}")
        else:
            print(f"❌ User not found: {username}")
    
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
