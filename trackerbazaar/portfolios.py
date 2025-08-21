import sqlite3
import json
from .tracker import Tracker

DB = "trackerbazaar.db"


class PortfolioManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS portfolios (
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (email, name)
                )
                """
            )
            conn.commit()

    def create_portfolio(self, name, email):
        """Create a new empty portfolio."""
        tracker = Tracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        """Save portfolio to DB (force JSON string)."""
        tracker_data = json.dumps(tracker.to_dict(), ensure_ascii=False)
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "REPLACE INTO portfolios(email, name, data) VALUES (?,?,?)",
                (email, name, tracker_data),
            )
            conn.commit()

    def load_portfolio(self, name, email):
        """Load a portfolio and reconstruct Tracker."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT data FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            row = c.fetchone()
            if row:
                try:
                    data = json.loads(row[0])
                    return Tracker.from_dict(data)
                except Exception:
                    return Tracker()
            return Tracker()

    def list_portfolios(self, email):
        """Return a list of portfolio names for this user."""
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT name FROM portfolios WHERE email=? ORDER BY name",
                (email,),
            )
            rows = c.fetchall()
            return [r[0] for r in rows] if rows else []
