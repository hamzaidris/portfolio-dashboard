import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256

DB = "trackerbazaar.db"

class UserManager:
    def __init__(self):
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
        if "logged_in_username" not in st.session_state:
            st.session_state.logged_in_username = None

    def _init_db(self):
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
        st.subheader("Sign Up")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            if not email or not password:
                st.error("Please fill all fields")
                return
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT email FROM users WHERE email=?", (email,))
                if c.fetchone():
                    st.error("User already exists")
                else:
                    c.execute("INSERT INTO users(email, password_hash) VALUES (?,?)",
                              (email, pbkdf2_sha256.hash(password)))
                    conn.commit()
                    st.success("Account created! Please login.")

    def login(self):
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
                row = c.fetchone()
                if row and pbkdf2_sha256.verify(password, row[0]):
                    st.session_state.logged_in_user = email
                    st.session_state.logged_in_username = email  # alias for old code
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    def logout(self):
        st.session_state.logged_in_user = None
        st.session_state.logged_in_username = None
        st.success("Logged out successfully!")
        st.rerun()
