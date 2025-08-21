import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256


class UserManager:
    def __init__(self):
        self.db_path = "trackerbazaar_v2.db"  # new DB file
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
            st.session_state.logged_in_username = None

    def _init_db(self):
        """Initialize users table and migrate schema if needed."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    username TEXT
                )
            """)
            conn.commit()

    def signup(self):
        st.subheader("Sign Up")
        email = st.text_input("Email", key="signup_email")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create Account"):
            if email and password:
                password_hash = pbkdf2_sha256.hash(password)
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    try:
                        c.execute(
                            "INSERT INTO users(email, password_hash, username) VALUES (?,?,?)",
                            (email, password_hash, username),
                        )
                        conn.commit()
                        st.success("Account created! Please login.")
                    except sqlite3.IntegrityError:
                        st.error("User already exists.")

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
                    st.session_state.logged_in_username = row[1] or email
                    st.rerun()
                else:
                    st.error("Invalid email or password")

    def logout(self):
        if st.sidebar.button("Logout"):
            st.session_state.logged_in_user = None
            st.session_state.logged_in_username = None
            st.rerun()

    def get_current_user(self):
        return st.session_state.logged_in_user
