import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256


class UserManager:
    def __init__(self):
        self.db_path = "trackerbazaar.db"
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
            st.session_state.logged_in_username = None

    def _init_db(self):
        """Initialize SQLite database with users table"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def signup(self):
        st.subheader("Sign Up")
        email = st.text_input("Email", key="signup_email")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create Account"):
            if not email or not username or not password:
                st.warning("Please fill out all fields.")
                return

            hashed = pbkdf2_sha256.hash(password)
            try:
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO users(email, username, password_hash) VALUES (?,?,?)",
                        (email, username, hashed),
                    )
                    conn.commit()
                st.success("Account created! Please log in.")
                st.rerun()  # ✅ replaced experimental_rerun
            except sqlite3.IntegrityError:
                st.error("An account with this email already exists.")

    def login(self):
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT password_hash, username FROM users WHERE email=?", (email,))
                row = c.fetchone()
                if row and pbkdf2_sha256.verify(password, row[0]):
                    st.session_state.logged_in_user = email
                    st.session_state.logged_in_username = row[1]
                    st.success("Login successful!")
                    st.rerun()  # ✅ replaced experimental_rerun
                else:
                    st.error("Invalid email or password.")
