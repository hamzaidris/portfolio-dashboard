import sqlite3
import hashlib

DB_PATH = "trackerbazaar.db"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Ensure users table exists with correct schema."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Fresh create
            cursor.execute("""
                CREATE TABLE users (
                    username TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    password TEXT
                )
            """)
            conn.commit()
        else:
            # Validate schema
            cursor.execute("PRAGMA table_info(users)")
            cols = [col[1] for col in cursor.fetchall()]
            expected = {"username", "email", "password"}
            if set(cols) != expected:
                # Drop and recreate if schema mismatch
                cursor.execute("DROP TABLE users")
                cursor.execute("""
                    CREATE TABLE users (
                        username TEXT PRIMARY KEY,
                        email TEXT UNIQUE,
                        password TEXT
                    )
                """)
                conn.commit()

def create_user(username: str, email: str, password: str):
    """Create a new user in the database."""
    if not username or not email or not password:
        return False  # reject empty values

    hashed_password = hash_password(password)
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username.strip(), email.strip(), hashed_password)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def login_user(username: str, password: str):
    """Validate user login."""
    if not username or not password:
        return None

    hashed_password = hash_password(password)
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, password FROM users WHERE username = ?", (username.strip(),))
        result = cursor.fetchone()
        if result:
            db_username, db_email, db_password = result
            if db_password == hashed_password:
                return {"username": db_username, "email": db_email}
    return None
