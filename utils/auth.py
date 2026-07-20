import streamlit as st
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

def init_session():
    """Initializes session state variables for authentication."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

def login_user(email: str, password: str) -> bool:
    """Attempts to log in a user. Returns True if successful."""
    user = get_user_by_email(email)
    if user and verify_password(password, user['password_hash']):
        st.session_state.logged_in = True
        st.session_state.user = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'organization': user['organization'],
            'role': user['role']
        }
        log_activity(email, 'Login Time', f"User {user['name']} logged in.")
        return True
    return False

def logout_user():
    """Logs out the current user."""
    st.session_state.logged_in = False
    st.session_state.user = None

def register_user(name: str, email: str, password: str, organization: str = "", role: str = "") -> bool:
    """Registers a new user. Returns True if successful, False if email exists."""
    password_hash = hash_password(password)
    return create_user(name, email, password_hash, organization, role)

def require_login():
    """
    To be called at the top of protected pages.
    Stops execution and shows a warning if the user is not logged in.
    Also injects global CSS to ensure UI consistency across all pages.
    """
    init_session()
    if not st.session_state.logged_in:
        st.warning("🔒 Please log in from the Home page to access this feature.")
        st.stop()
        
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
