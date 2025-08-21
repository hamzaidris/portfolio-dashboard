import sqlite3
import os

# ✅ Single source of truth for DB file
DB_FILE = "trackerbazaar_v3.db"

# ✅ Central schema definitions
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
            FOREIGN KEY(owner_email) REFERENCES users(email)
        )
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            type TEXT CHECK(type IN ('buy', 'sell')) NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
        )
    """,
    "dividends": """
        CREATE TABLE IF NOT EXISTS dividends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
        )
    """,
    "cash": """
        CREATE TABLE IF NOT EXISTS cash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT CHECK(type IN ('deposit','withdraw')) NOT NULL,
            FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
        )
    """
}

def init_db():
    """Initialize database with schema."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for name, ddl in TABLES.items():
            cursor.execute(ddl)
        conn.commit()
