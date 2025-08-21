import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256

DB = "trackerbazaar.db"


class UserManager:
    def __init__(self):
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None

    def _init_db(self):
        """Ensure the users table exists."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def signup(self):
        st.subheader("Create Account")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Sign Up"):
            if not email or not password:
                st.error("Please enter both email and password.")
                return

            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT email FROM users WHERE email=?", (email,))
                if c.fetchone():
                    st.error("User already exists. Try logging in.")
                    return

                password_hash = pbkdf2_sha256.hash(password)
                c.execute("INSERT INTO users(email, password_hash) VALUES (?,?)",
                          (email, password_hash))
                conn.commit()

            st.success("Account created. Please log in.")
            st.rerun()

    def login(self):
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            if not email or not password:
                st.error("Please enter both email and password.")
                return

            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
                row = c.fetchone()

            if row and pbkdf2_sha256.verify(password, row[0]):
                st.session_state.logged_in_user = email
                st.success(f"Welcome, {email}!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    def logout(self):
        if st.button("Logout"):
            st.session_state.logged_in_user = None
            st.success("Logged out successfully.")
            st.rerun()

    def get_current_user(self):
        return st.session_state.get("logged_in_user")
