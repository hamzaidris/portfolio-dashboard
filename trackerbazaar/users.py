import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256

DB_FILE = "trackerbazaar_v2.db"  # ✅ consistent with other modules


class UserManager:
    def __init__(self):
        self._init_db()
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None

    def _init_db(self):
        """Initialize the users table inside trackerbazaar_v2.db"""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def signup(self, email, password):
        """Register a new user."""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                password_hash = pbkdf2_sha256.hash(password)
                c.execute(
                    "INSERT INTO users(email, password_hash) VALUES (?, ?)",
                    (email, password_hash),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            st.error("User already exists.")
            return False
        except Exception as e:
            st.error(f"Signup failed: {e}")
            return False

    def login(self, email, password):
        """Login existing user."""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
                row = c.fetchone()

                if row and pbkdf2_sha256.verify(password, row[0]):
                    st.session_state.logged_in_user = email
                    return True
                else:
                    st.error("Invalid email or password.")
                    return False
        except Exception as e:
            st.error(f"Login failed: {e}")
            return False

    def logout(self):
        """Logout user."""
        st.session_state.logged_in_user = None

    def get_current_user(self):
        """Return logged in user email or None."""
        return st.session_state.get("logged_in_user", None)

    def login_signup_panel(self):
        """UI Panel for login/signup inside Streamlit."""
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                if self.login(email, password):
                    st.success("Logged in successfully!")
                    st.rerun()

        with tab_signup:
            st.subheader("Sign Up")
            email = st.text_input("New Email", key="signup_email")
            password = st.text_input("New Password", type="password", key="signup_password")
            if st.button("Sign Up"):
                if self.signup(email, password):
                    st.success("Account created! Please log in.")
