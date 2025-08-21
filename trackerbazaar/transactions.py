import sqlite3
from datetime import datetime

DB_FILE = "trackerbazaar_v2.db"  # ✅ new DB

def init_transactions_table():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                portfolio_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                type TEXT CHECK(type IN ('buy','sell')) NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()

def add_transaction(email, portfolio_name, ticker, quantity, price, tx_type):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO transactions (email, portfolio_name, ticker, quantity, price, type, timestamp) VALUES (?,?,?,?,?,?,?)",
            (email, portfolio_name, ticker, quantity, price, tx_type, datetime.now().isoformat())
        )
        conn.commit()

def get_transactions(email, portfolio_name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT ticker, quantity, price, type, timestamp FROM transactions WHERE email=? AND portfolio_name=? ORDER BY id DESC", (email, portfolio_name))
        return c.fetchall()

# Initialize on import
init_transactions_table()
