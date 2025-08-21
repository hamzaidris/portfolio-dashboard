import sqlite3
import streamlit as st
from passlib.hash import pbkdf2_sha256

DB = "trackerbazaar.db"


class UserManager:
    def __init__(self):
        self._ensure_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
        if "logged_in_username" not in st.session_state:
            st.session_state.logged_in_username = None

    def _ensure_db(self):
        """Ensure the users table exists with email, password_hash, and username."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    username TEXT
                )
                """
            )
            conn.commit()

    # ---------------------- SIGNUP ----------------------
    def signup(self):
        """Render signup form and create a new user."""
        st.subheader("Create a New Account")

        email = st.text_input("Email")
        username = st.text_input("Username (optional)")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if password != confirm:
                st.error("Passwords do not match ❌")
                return

            password_hash = pbkdf2_sha256.hash(password)
            try:
                with sqlite3.connect(DB) as conn:
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO users(email, password_hash, username) VALUES (?,?,?)",
                        (email, password_hash, username),
                    )
                    conn.commit()
                st.success("✅ Account created. Please log in now.")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("❌ This email is already registered.")

    # ---------------------- LOGIN ----------------------
    def login(self):
        """Render login form and log in a user."""
        st.subheader("Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT password_hash, username FROM users WHERE email=?", (email,))
                row = c.fetchone()

            if row and pbkdf2_sha256.verify(password, row[0]):
                st.session_state.logged_in_user = email
                st.session_state.logged_in_username = row[1] if row[1] else email
                st.success(f"✅ Logged in as {st.session_state.logged_in_username}")
                st.rerun()
            else:
                st.error("❌ Invalid email or password")

    # ---------------------- LOGOUT ----------------------
    def logout(self):
        """Log out the current user."""
        st.session_state.logged_in_user = None
        st.session_state.logged_in_username = None
        st.success("✅ Logged out")
        st.rerun()

    # ---------------------- HELPERS ----------------------
    def get_current_user(self):
        return st.session_state.get("logged_in_user")

    def get_current_username(self):
        return st.session_state.get("logged_in_username")
