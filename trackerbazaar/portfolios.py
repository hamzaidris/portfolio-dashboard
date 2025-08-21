import sqlite3
import json
from trackerbazaar.tracker import Tracker


class PortfolioManager:
    def __init__(self, db_path="trackerbazaar_v2.db"):  # switched to new DB file
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Ensure the portfolios table exists with correct schema"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT
                )
                """
            )
            conn.commit()

    def create_portfolio(self, name, email):
        tracker = Tracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        tracker_data = json.dumps(tracker.to_dict())
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO portfolios(email, name, data) VALUES (?,?,?)",
                (email, name, tracker_data),
            )
            conn.commit()

    def load_portfolio(self, name, email):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT data FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            row = c.fetchone()
            if row:
                data = json.loads(row[0])
                return Tracker.from_dict(data)
        return None

    def list_portfolios(self, email):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT name FROM portfolios WHERE email=? ORDER BY name",
                (email,),
            )
            return [row[0] for row in c.fetchall()]
