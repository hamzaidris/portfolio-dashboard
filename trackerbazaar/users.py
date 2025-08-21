import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256


class UserManager:
    def __init__(self, db_path="trackerbazaar.db"):
        self.db_path = db_path
        self._init_db()

        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
        if "logged_in_username" not in st.session_state:
            st.session_state.logged_in_username = None

    def _init_db(self):
        """Ensure users table exists"""
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
        st.subheader("Sign Up")
        email = st.text_input("Email (for signup)", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            if email and password:
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    try:
                        c.execute(
                            "INSERT INTO users(email, password_hash) VALUES (?, ?)",
                            (email, pbkdf2_sha256.hash(password)),
                        )
                        conn.commit()
                        st.success("Account created! Please login.")
                    except sqlite3.IntegrityError:
                        st.error("Email already exists.")
            else:
                st.warning("Please enter email and password.")

    def login(self):
        st.subheader("Login")
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
                    st.success(f"Welcome {st.session_state.logged_in_username} 👋")
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password.")

    def logout(self):
        if st.button("Logout"):
            st.session_state.logged_in_user = None
            st.session_state.logged_in_username = None
            st.experimental_rerun()

    def get_current_user(self):
        return st.session_state.get("logged_in_user", None)
