import sqlite3
import json
from tracker import Tracker  # adjust if path differs

DB = "trackerbazaar.db"


class PortfolioManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Ensure the portfolios table exists."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT,
                    PRIMARY KEY (email, name)
                )
            """)
            conn.commit()

    def create_portfolio(self, name, email):
        tracker = Tracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "REPLACE INTO portfolios(email, name, data) VALUES (?,?,?)",
                (email, name, json.dumps(tracker.to_dict())),
            )
            conn.commit()

    def load_portfolio(self, name, email):
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT data FROM portfolios WHERE email=? AND name=?", (email, name))
            row = c.fetchone()
            if row:
                return Tracker.from_dict(json.loads(row[0]))
            return None

    def list_portfolios(self, email):
        if not email:
            return []
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM portfolios WHERE email=? ORDER BY name", (email,))
            rows = c.fetchall()
            return [r[0] for r in rows] if rows else []
