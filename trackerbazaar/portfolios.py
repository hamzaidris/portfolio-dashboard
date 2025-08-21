import sqlite3
import json
from tracker import PortfolioTracker

DB_FILE = "trackerbazaar_v2.db"  # ✅ new DB

def init_portfolios_table():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                data TEXT,
                UNIQUE(email, name)
            )
        """)
        conn.commit()

def save_portfolio(email, name, tracker):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        tracker_data = json.dumps(tracker.to_dict())
        c.execute(
            "REPLACE INTO portfolios(email, name, data) VALUES (?,?,?)",
            (email, name, tracker_data)
        )
        conn.commit()

def load_portfolio(email, name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT data FROM portfolios WHERE email=? AND name=?", (email, name))
        row = c.fetchone()
        if row:
            return PortfolioTracker.from_dict(json.loads(row[0]))
    return None

def list_portfolios(email):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM portfolios WHERE email=? ORDER BY name", (email,))
        return [r[0] for r in c.fetchall()]

# Initialize on import
init_portfolios_table()
