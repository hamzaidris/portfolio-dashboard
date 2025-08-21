import sqlite3
import json
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ renamed import
from trackerbazaar.data import DB_FILE


class PortfolioManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Initialize the portfolios table in the database."""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (email, name)
                )
            """)
            conn.commit()

    def create_portfolio(self, name, email):
        """Create a new portfolio for the user."""
        tracker = PortfolioTracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        """Save or update a portfolio in the database."""
        tracker_data = json.dumps(tracker.to_dict())
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "REPLACE INTO portfolios(email, name, data) VALUES (?, ?, ?)",
                (email, name, tracker_data),
            )
            conn.commit()

    def load_portfolio(self, name, email):
        """Load a portfolio by name for a specific user."""
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
        """List all portfolio names for a specific user."""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT name FROM portfolios WHERE email=? ORDER BY name",
                (email,),
            )
            return [row[0] for row in c.fetchall()]

    def delete_portfolio(self, name, email):
        """Delete a portfolio."""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "DELETE FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            conn.commit()
