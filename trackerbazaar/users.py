import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.db_path = "trackerbazaar.db"
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
        if "logged_in_username" not in st.session_state:
            st.session_state.logged_in_username = None

    def _init_db(self):
        """Initialize SQLite database with users table and handle schema migration if needed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if table exists and has the correct columns
                cursor.execute("PRAGMA table_info(users)")
                columns = {row[1] for row in cursor.fetchall()}
                logger.info(f"Existing columns in users table: {columns}")
                if not columns or {"email", "password_hash", "username"} - columns:
                    logger.info("Recreating users table due to missing columns.")
                    # Backup existing data if table exists
                    if columns:
                        cursor.execute("SELECT email, username FROM users")
                        existing_users = [(row[0], row[1] if row[1] else "") for row in cursor.fetchall()]
                        if existing_users:
                            logger.warning(f"Backing up {len(existing_users)} existing users before recreating table.")
                            backup_table = "users_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
                            cursor.execute(f"ALTER TABLE users RENAME TO {backup_table}")
                    # Recreate the table with username
                    cursor.execute("""
                        CREATE TABLE users (
                            email TEXT NOT NULL,
                            username TEXT NOT NULL,
                            password_hash TEXT NOT NULL,
                            PRIMARY KEY (email)
                        )
                    """)
                    conn.commit()
                    # Restore backed-up data with empty username/password_hash if missing (users must re-signup)
                    if existing_users:
                        for email, username in existing_users:
                            cursor.execute("INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)", 
                                           (email, username if username else "", ""))
                    st.warning("Database schema recreated. Please re-signup with your email and username to set a new password.")
                else:
                    logger.info("Users table schema is correct.")
                conn.commit()
        except sqlite3.OperationalError as e:
            logger.error(f"Failed to initialize database: {e}")
            st.error(f"Failed to initialize database: {e}. Please check file permissions or contact support.")
        except Exception as e:
            logger.error(f"Unexpected error initializing database: {e}")
            st.error(f"Unexpected error initializing database: {e}. Please try again later.")

    def login(self):
        """Render login form and handle authentication using either email or username."""
        st.header("Login")
        identifier = st.text_input("Email or Username", key="login_identifier")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_submit"):
            if not identifier or not password:
                st.error("Identifier and password cannot be empty.")
                return
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    # Check if identifier is an email or username
                    cursor.execute("SELECT password_hash, username, email FROM users WHERE email = ? OR username = ?", (identifier, identifier))
                    result = cursor.fetchone()
                    if result:
                        stored_hash, stored_username, stored_email = result
                        try:
                            if pbkdf2_sha256.verify(password, stored_hash):
                                st.session_state.logged_in_user = stored_email
                                st.session_state.logged_in_username = stored_username
                                st.success(f"Logged in as {stored_username} ({stored_email})")
                                st.rerun()
                            else:
                                st.error("Invalid identifier or password")
                        except ValueError:
                            st.error("Invalid password hash for this account. Please re-signup with this email and username to reset your password.")
                    else:
                        st.error("Invalid identifier or password")
            except sqlite3.OperationalError as e:
                logger.error(f"Database error during login: {e}")
                st.error(f"Database error during login: {e}. Please try again or contact support.")
            except Exception as e:
                logger.error(f"Unexpected error during login: {e}")
                st.error(f"Unexpected error during login: {e}. Please try again later.")

    def logout(self):
        """Render logout button in sidebar for logged-in users."""
        if st.sidebar.button("Logout", key="logout_submit"):
            st.session_state.logged_in_user = None
            st.session_state.logged_in_username = None
            st.session_state.portfolios = {}
            st.session_state.selected_portfolio = None
            st.success("Logged out successfully")
            st.rerun()

    def signup(self):
        """Render signup form and add new user to database."""
        st.header("Sign Up")
        st.write("Create a new account to manage your portfolios.")
        new_email = st.text_input("New Email", key="signup_email")
        new_username = st.text_input("New Username", key="signup_username")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        
        if st.button("Sign Up", key="signup_submit"):
            if not new_email or not new_username or not new_password:
                st.error("Email, username, and password cannot be empty.")
                return
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT email FROM users WHERE email = ?", (new_email,))
                    if cursor.fetchone():
                        st.error("Email already registered. Please use a different email or log in.")
                        return
                    cursor.execute("SELECT username FROM users WHERE username = ?", (new_username,))
                    if cursor.fetchone():
                        st.error("Username already taken. Please choose a different username.")
                        return
                    password_hash = pbkdf2_sha256.hash(new_password)
                    cursor.execute("INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)", 
                                   (new_email, new_username, password_hash))
                    conn.commit()
                    st.session_state.logged_in_user = new_email
                    st.session_state.logged_in_username = new_username
                    st.success(f"Account created for {new_username} ({new_email}). You are now logged in.")
                    st.rerun()
            except sqlite3.OperationalError as e:
                logger.error(f"Database error during signup: {e}")
                st.error(f"Database error during signup: {e}. Please try again or contact support.")
            except Exception as e:
                logger.error(f"Unexpected error during signup: {e}")
                st.error(f"Unexpected error during signup: {e}. Please try again later.")

    def is_logged_in(self):
        """Check if a user is logged in."""
        return st.session_state.logged_in_user is not None

    def get_current_user(self):
        """Get the email of the currently logged-in user."""
        return st.session_state.logged_in_user

    def get_current_username(self):
        """Get the username of the currently logged-in user."""
        return st.session_state.logged_in_username
