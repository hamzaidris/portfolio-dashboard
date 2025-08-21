import sqlite3
import streamlit as st
from passlib.hash import pbkdf2_sha256

DB = "trackerbazaar.db"

def _init_users():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT,
            password_hash TEXT NOT NULL
        )
        """)
        conn.commit()

class UserManager:
    def __init__(self):
        _init_users()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
        if "logged_in_username" not in st.session_state:
            st.session_state.logged_in_username = None

    def is_logged_in(self) -> bool:
        return st.session_state.logged_in_user is not None

    def get_current_user(self):
        return st.session_state.logged_in_user

    def get_current_username(self):
        return st.session_state.logged_in_username or ""

    def signup(self):
        st.subheader("Sign Up")
        with st.form("signup_form", clear_on_submit=False):
            email = st.text_input("Email")
            username = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            submit = st.form_submit_button("Create Account")
        if submit:
            if not email or not pwd:
                st.error("Email and password are required.")
                return
            ph = pbkdf2_sha256.hash(pwd)
            try:
                with sqlite3.connect(DB) as conn:
                    c = conn.cursor()
                    c.execute("INSERT INTO users(email, username, password_hash) VALUES(?,?,?)", (email, username, ph))
                    conn.commit()
                st.success("Account created. Please log in.")
            except sqlite3.IntegrityError:
                st.error("Email already exists. Try logging in.")

    def login(self):
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
        if submit:
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("SELECT password_hash, username FROM users WHERE email = ?", (email,))
                row = c.fetchone()
            if row and pbkdf2_sha256.verify(pwd, row[0]):
                st.session_state.logged_in_user = email
                st.session_state.logged_in_username = row[1] or email.split("@")[0]
                st.success("Logged in.")
            else:
                st.error("Invalid credentials.")

    def logout(self):
        if st.button("Logout"):
            st.session_state.logged_in_user = None
            st.session_state.logged_in_username = None
            st.experimental_rerun()
