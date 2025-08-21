import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
from trackerbazaar.data import DB_FILE

class UserManager:
    def __init__(self):
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None

    def _init_db(self):
        """Initialize users table if it doesn't exist"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def register_user(self, email, password):
        """Register a new user"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                return False, "❌ User already exists"
            password_hash = pbkdf2_sha256.hash(password)
            cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)",
                           (email, password_hash))
            conn.commit()
        return True, "✅ User registered successfully"

    def login_user(self, email, password):
        """Check login credentials"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE email=?", (email,))
            row = cursor.fetchone()
            if row and pbkdf2_sha256.verify(password, row[0]):
                st.session_state.logged_in_user = email
                return True, "✅ Login successful"
            return False, "❌ Invalid credentials"

    def logout(self):
        st.session_state.logged_in_user = None

    def is_logged_in(self):
        return st.session_state.logged_in_user is not None

    def login_form(self):
        """Render login/register UI"""
        st.subheader("Login")

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

            if login_btn:
                ok, msg = self.login_user(email, password)
                st.info(msg)
                if ok:
                    st.rerun()

        st.divider()
        st.subheader("Register")

        with st.form("register_form"):
            reg_email = st.text_input("New Email")
            reg_password = st.text_input("New Password", type="password")
            register_btn = st.form_submit_button("Register")

            if register_btn:
                ok, msg = self.register_user(reg_email, reg_password)
                st.info(msg)
