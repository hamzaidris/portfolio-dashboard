import sqlite3
import json
from trackerbazaar.tracker import PortfolioTracker  # fixed import

DB_FILE = "trackerbazaar_v2.db"  # ✅ consistent everywhere


class PortfolioManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_FILE) as conn:
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

    def save_portfolio(self, name, email, tracker: PortfolioTracker):
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

    def create_portfolio(self, name, email):
        tracker = PortfolioTracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def list_portfolios(self, email):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("SELECT name FROM portfolios WHERE email=? ORDER BY name", (email,))
                return [row[0] for row in c.fetchall()]
        except Exception as e:
            raise RuntimeError(f"Database error while loading portfolios: {e}")

    def load_portfolio(self, name, email):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("SELECT data FROM portfolios WHERE email=? AND name=?", (email, name))
                row = c.fetchone()
                if row and row[0]:
                    return PortfolioTracker.from_dict(json.loads(row[0]))
                else:
                    return PortfolioTracker()
        except Exception as e:
            raise RuntimeError(f"Failed to load portfolio: {e}")
