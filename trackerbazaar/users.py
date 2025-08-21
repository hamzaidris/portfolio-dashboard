import streamlit as st
import sqlite3
import hashlib

DB_PATH = "trackerbazaar.db"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Ensure users table exists with correct schema."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Fresh create
            cursor.execute("""
                CREATE TABLE users (
                    username TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    password TEXT
                )
            """)
            conn.commit()
        else:
            # Validate schema
            cursor.execute("PRAGMA table_info(users)")
            cols = [col[1] for col in cursor.fetchall()]
            expected = {"username", "email", "password"}
            if set(cols) != expected:
                # Drop and recreate if schema mismatch
                cursor.execute("DROP TABLE users")
                cursor.execute("""
                    CREATE TABLE users (
                        username TEXT PRIMARY KEY,
                        email TEXT UNIQUE,
                        password TEXT
                    )
                """)
                conn.commit()

class UserManager:
    def __init__(self):
        init_db()
        if 'user' not in st.session_state:
            st.session_state.user = None
    
    def login(self):
        """Render login form."""
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if self.authenticate(username, password):
                    st.session_state.user = username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    def signup(self):
        """Render signup form."""
        with st.form("signup_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif self.create_user(username, email, password):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username or email already exists")
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user."""
        if not username or not password:
            return False
            
        hashed_password = hash_password(password)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                # FIXED: Use 'password' column instead of 'password_hash'
                cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                if result and result[0] == hashed_password:
                    return True
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
        return False
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user."""
        if not username or not email or not password:
            return False
            
        hashed_password = hash_password(password)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, hashed_password)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return False
    
    def logout(self):
        """Logout user."""
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return st.session_state.user is not None
    
    def get_current_user(self) -> str:
        """Get current username."""
        return st.session_state.user
