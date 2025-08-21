# trackerbazaar/data.py

import sqlite3
import os

DB_FILE = "trackerbazaar_v2.db"


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_db():
    """
    Initialize database with all required tables.
    Also handles migrations (e.g., adding missing columns).
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # ✅ Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)

        # ✅ Portfolios table (with owner_email)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                owner_email TEXT NOT NULL,
                FOREIGN KEY (owner_email) REFERENCES users(email)
            )
        """)

        # ✅ Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                transaction_type TEXT NOT NULL, -- buy/sell
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                brokerage REAL DEFAULT 0,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
            )
        """)

        # ✅ Dividends table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
            )
        """)

        # ✅ Cash table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cash (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
            )
        """)

        # --- 🔧 MIGRATIONS ---
        # Add `owner_email` column if missing (older DBs might not have it)
        cursor.execute("PRAGMA table_info(portfolios)")
        cols = [row[1] for row in cursor.fetchall()]
        if "owner_email" not in cols:
            cursor.execute("ALTER TABLE portfolios ADD COLUMN owner_email TEXT DEFAULT 'unknown'")

        conn.commit()
