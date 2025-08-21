import sqlite3
import hashlib

DB_PATH = "trackerbazaar.db"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, email: str, password: str):
    """Create a new user in the database."""
    hashed_password = hash_password(password)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password TEXT
            )
        """)
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def login_user(username: str, password: str):
    """Validate user login."""
    hashed_password = hash_password(password)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            db_username, db_email, db_password = result
            if db_password == hashed_password:
                return {"username": db_username, "email": db_email}
    return None
