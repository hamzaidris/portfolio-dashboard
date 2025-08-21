import sqlite3
import json
from .tracker import Tracker   # adjusted import

DB = "trackerbazaar.db"


class PortfolioManager:
    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        """Ensure the portfolios table exists."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT,
                    UNIQUE(email, name)
                )
                """
            )
            conn.commit()

    def create_portfolio(self, name, email):
        """Create a new portfolio for the given user."""
        tracker = Tracker()  # start fresh
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        """Save or replace a portfolio."""
        tracker_data = json.dumps(tracker.to_dict())
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT OR REPLACE INTO portfolios (id, email, name, data)
                VALUES (
                    COALESCE(
                        (SELECT id FROM portfolios WHERE email=? AND name=?),
                        NULL
                    ),
                    ?, ?, ?
                )
                """,
                (email, name, email, name, tracker_data),
            )
            conn.commit()

    def load_portfolio(self, name, email):
        """Load a portfolio and return Tracker object."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT data FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            row = c.fetchone()
        if row:
            data = json.loads(row[0])
            return Tracker.from_dict(data)
        return Tracker()

    def list_portfolios(self, email):
        """List all portfolio names for a given user."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT name FROM portfolios WHERE email=? ORDER BY name",
                (email,),
            )
            rows = c.fetchall()
        return [r[0] for r in rows]
