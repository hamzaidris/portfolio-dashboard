# trackerbazaar/portfolios.py
import sqlite3
import json
from trackerbazaar.tracker import PortfolioTracker   # ✅ absolute import
from trackerbazaar.data import DB_FILE               # ✅ consistent DB file

class PortfolioManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Ensure portfolios table exists."""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS portfolios (
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT,
                    PRIMARY KEY (email, name)
                )
                """
            )
            conn.commit()

    def create_portfolio(self, name, email):
        """Create a new portfolio and save to DB."""
        tracker = PortfolioTracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        """Save portfolio tracker object to DB."""
        try:
            tracker_data = json.dumps(tracker.to_dict())
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute(
                    "REPLACE INTO portfolios(email, name, data) VALUES (?,?,?)",
                    (email, name, tracker_data),
                )
                conn.commit()
        except Exception as e:
            raise RuntimeError(f"Failed to save portfolio: {e}")

    def load_portfolio(self, name, email):
        """Load portfolio by name + email from DB."""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT data FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            row = c.fetchone()
            if row:
                data = json.loads(row[0])
                return PortfolioTracker.from_dict(data)
            return None

    def list_portfolios(self, email):
        """List all portfolio names for a user."""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT name FROM portfolios WHERE email=? ORDER BY name",
                (email,),
            )
            rows = c.fetchall()
            return [row[0] for row in rows]

    def delete_portfolio(self, name, email):
        """Delete a portfolio from DB."""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "DELETE FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            conn.commit()
