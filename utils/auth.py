import hashlib
import secrets
from utils.db import create_user, get_user_by_email, update_user_password, log_activity

def hash_password(password: str, salt: str = None) -> str:
    """Hashes a password with a salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode('utf-8'))
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(password: str, password_hash: str) -> bool:
    """Verifies a password against a stored hash."""
    try:
        salt, expected_hash = password_hash.split('$')
        actual_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        return actual_hash == expected_hash
    except ValueError:
        return False

def register_user(name: str, email: str, password: str, organization: str = "", role: str = "") -> bool:
    """Registers a new user. Returns True if successful, False if email exists."""
    password_hash = hash_password(password)
    return create_user(name, email, password_hash, organization, role)
