import sqlite3
from passlib.hash import pbkdf2_sha256
import streamlit as st

DB = "trackerbazaar.db"


class UserManager:
    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        """Ensure users table exists."""
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

    def signup(self, email, password, username=None):
        self._ensure_db()
        password_hash = pbkdf2_sha256.hash(password)
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            try:
                c.execute(
                    "INSERT INTO users(email, password_hash, username) VALUES (?,?,?)",
                    (email, password_hash, username),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def login(self):
        self._ensure_db()
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT password_hash, username FROM users WHERE email=?",
                    (email,),
                )
                row = c.fetchone()
                if row and pbkdf2_sha256.verify(password, row[0]):
                    st.session_state.logged_in_user = email
                    st.session_state.logged_in_username = row[1] or email.split("@")[0]
                    st.success("Login successful ✅")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    def get_current_user(self):
        return getattr(st.session_state, "logged_in_user", None)

    def logout(self):
        st.session_state.logged_in_user = None
        st.session_state.logged_in_username = None
        st.rerun()
