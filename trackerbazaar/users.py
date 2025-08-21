import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256

DB_FILE = "trackerbazaar_v2.db"  # ✅ new DB

def init_users_table():
    """Ensure users table exists."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()

def signup(email, password):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        password_hash = pbkdf2_sha256.hash(password)
        try:
            c.execute("INSERT INTO users (email, password_hash) VALUES (?,?)", (email, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def login(email, password):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE email=?", (email,))
        row = c.fetchone()
        if row and pbkdf2_sha256.verify(password, row[0]):
            return True
    return False

# Initialize on import
init_users_table()
