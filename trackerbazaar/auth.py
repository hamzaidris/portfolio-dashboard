import sqlite3
import hashlib

def login_user(username, password):
    """Authenticate user and return user data."""
    # Hash password for comparison (example; adjust to your hashing method)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect('trackerbazaar.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, password FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {'username': user[0], 'email': user[1]}
    return None
