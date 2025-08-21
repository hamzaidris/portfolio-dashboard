# trackerbazaar/data.py
import sqlite3
import os

# ✅ Single DB file reference (easy to change later)
DB_FILE = "trackerbazaar_v3.db"

# ✅ Schema definitions
TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """,
    "portfolios": """
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            owner_email TEXT NOT NULL,
            FOREIGN KEY (owner_email) REFERENCES users(email)
        )
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            ticker TEXT,
            quantity REAL,
            price REAL,
            date TEXT,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        )
    """,
    "dividends": """
        CREATE TABLE IF NOT EXISTS dividends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            ticker TEXT,
            amount REAL,
            date TEXT,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        )
    """,
    "cash": """
        CREATE TABLE IF NOT EXISTS cash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            amount REAL,
            date TEXT,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        )
    """
}

def init_db():
    """Initialize the database and create tables if they don’t exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # ✅ Execute each CREATE TABLE individually
    for name, ddl in TABLES.items():
        try:
            cursor.execute(ddl)
        except sqlite3.Error as e:
            print(f"⚠️ Failed creating table {name}: {e}")

    conn.commit()
    conn.close()
