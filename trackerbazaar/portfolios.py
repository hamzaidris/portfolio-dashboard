import sqlite3
import json
from trackerbazaar.tracker import PortfolioTracker  # ✅ correct package import

DB_FILE = "trackerbazaar_v2.db"


class PortfolioManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Initialize the portfolios table in trackerbazaar_v2.db"""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    UNIQUE(email, name)
                )
                """
            )
            conn.commit()

    def save_portfolio(self, name, email, tracker):
        """Save or update portfolio"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                tracker_data = json.dumps(tracker.to_dict())
                c.execute(
                    "REPLACE INTO portfolios(email, name, data) VALUES (?,?,?)",
                    (email, name, tracker_data),
                )
                conn.commit()
        except Exception as e:
            raise RuntimeError(f"Failed to save portfolio: {e}")

    def load_portfolio(self, name, email):
        """Load portfolio by name"""
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT data FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            row = c.fetchone()
            if row:
                return PortfolioTracker.from_dict(json.loads(row[0]))
        return None

    def list_portfolios(self, email):
        """List all portfolio names for a user"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT name FROM portfolios WHERE email=? ORDER BY name",
                    (email,),
                )
                return [row[0] for row in c.fetchall()]
        except Exception as e:
            raise RuntimeError(f"Database error while loading portfolios: {e}")

    def create_portfolio(self, name, email):
        """Create a new portfolio and return it"""
        tracker = PortfolioTracker()
        self.save_portfolio(name, email, tracker)
        return tracker
