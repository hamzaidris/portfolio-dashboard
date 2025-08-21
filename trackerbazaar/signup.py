import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256


def init_db():
    """Ensure users table exists with correct schema"""
    with sqlite3.connect("trackerbazaar.db") as conn:
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


def signup():
    st.subheader("Sign Up")

    email = st.text_input("Email", key="signup_email")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Create Account"):
        if not email or not username or not password:
            st.warning("Please fill out all fields.")
            return

        hashed_pw = pbkdf2_sha256.hash(password)
        try:
            with sqlite3.connect("trackerbazaar.db") as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users(email, username, password_hash) VALUES (?,?,?)",
                    (email, username, hashed_pw),
                )
                conn.commit()

            st.success("Account created! Please log in.")
            st.rerun()  # ✅ replaced experimental_rerun

        except sqlite3.IntegrityError:
            st.error("An account with this email already exists.")


# Run initialization when this module is imported
init_db()
