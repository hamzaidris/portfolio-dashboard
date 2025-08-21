import sqlite3
from datetime import datetime

DB_FILE = "trackerbazaar_v2.db"  # ✅ new DB

def init_dividends_table():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS dividends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                portfolio_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()

def add_dividend(email, portfolio_name, ticker, amount):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO dividends (email, portfolio_name, ticker, amount, timestamp) VALUES (?,?,?,?,?)",
            (email, portfolio_name, ticker, amount, datetime.now().isoformat())
        )
        conn.commit()

def get_dividends(email, portfolio_name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT ticker, amount, timestamp FROM dividends WHERE email=? AND portfolio_name=? ORDER BY id DESC",
            (email, portfolio_name)
        )
        return c.fetchall()

# Initialize
init_dividends_table()
