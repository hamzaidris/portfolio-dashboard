import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
from datetime import datetime

class UserManager:
    def __init__(self):
        self.db_path = "trackerbazaar.db"
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None

    def _init_db(self):
        """Initialize SQLite database with users table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def login(self):
        """Render login form and handle authentication."""
        st.sidebar.header("User Login")
        email = st.sidebar.text_input("Email", key="login_email")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Login", key="login_submit"):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
                result = cursor.fetchone()
                if result and pbkdf2_sha256.verify(password, result[0]):
                    st.session_state.logged_in_user = email
                    st.success(f"Logged in as {email}")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid email or password")
        if st.sidebar.button("Logout", key="logout_submit") and st.session_state.logged_in_user:
            st.session_state.logged_in_user = None
            st.session_state.portfolios = {}
            st.success("Logged out successfully")
            st.rerun()

    def signup(self):
        """Render signup form and add new user to database."""
        st.header("Sign Up")
        st.write("Create a new account to manage your portfolios.")
        new_email = st.text_input("New Email", key="signup_email")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        
        if st.button("Sign Up", key="signup_submit"):
            if not new_email or not new_password:
                st.error("Email and password cannot be empty.")
                return
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM users WHERE email = ?", (new_email,))
                if cursor.fetchone():
                    st.error("Email already registered. Please use a different email or log in.")
                    return
                password_hash = pbkdf2_sha256.hash(new_password)
                cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (new_email, password_hash))
                conn.commit()
                st.session_state.logged_in_user = new_email
                st.success(f"Account created for {new_email}. You are now logged in.")
                st.rerun()

    def is_logged_in(self):
        """Check if a user is logged in."""
        return st.session_state.logged_in_user is not None

    def get_current_user(self):
        """Get the email of the currently logged-in user."""
        return st.session_state.logged_in_user
