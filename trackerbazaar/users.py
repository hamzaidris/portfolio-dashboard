import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256

DB_PATH = "trackerbazaar_v2.db"

class UserManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
        if "logged_in_username" not in st.session_state:
            st.session_state.logged_in_username = None

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def signup(self):
        st.write("Create a new account")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            if not email or not password:
                st.warning("Email and password required.")
                return
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                try:
                    password_hash = pbkdf2_sha256.hash(password)
                    c.execute("INSERT INTO users(email, password_hash) VALUES(?, ?)", (email, password_hash))
                    conn.commit()
                    st.success("Account created! Please login.")
                except sqlite3.IntegrityError:
                    st.error("User already exists!")

    def login(self):
        st.write("Login to your account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
                row = c.fetchone()
                if row and pbkdf2_sha256.verify(password, row[0]):
                    st.session_state.logged_in_user = email
                    st.session_state.logged_in_username = email.split("@")[0]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
