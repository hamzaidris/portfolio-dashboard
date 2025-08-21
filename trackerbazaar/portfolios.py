import sqlite3
import json
from trackerbazaar.tracker import Tracker

DB_PATH = "trackerbazaar_v2.db"

class PortfolioManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT,
                    FOREIGN KEY (email) REFERENCES users(email)
                )
            """)
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
                "INSERT INTO portfolios(email, name, data) VALUES (?,?,?)",
                (email, name, tracker_data)
            )
            conn.commit()

    def list_portfolios(self, email):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM portfolios WHERE email=? ORDER BY name", (email,))
            rows = c.fetchall()
            return [r[0] for r in rows]

    def load_portfolio(self, email, name):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT data FROM portfolios WHERE email=? AND name=?", (email, name))
            row = c.fetchone()
            if row:
                return Tracker.from_dict(json.loads(row[0]))
            return None
