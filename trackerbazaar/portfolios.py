import sqlite3, json
from trackerbazaar.tracker import PortfolioTracker

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
                    email TEXT,
                    name TEXT,
                    data TEXT,
                    PRIMARY KEY(email, name)
                )
            """)
            conn.commit()

    def create_portfolio(self, name, email):
        if not email:
            raise ValueError("No user logged in")
        tracker = PortfolioTracker(name)
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        if not email:
            return
        data = json.dumps(tracker.to_dict())
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute(
                "REPLACE INTO portfolios(email, name, data) VALUES (?,?,?)",
                (email, name, data)
            )
            conn.commit()

    def load_portfolio(self, name, email):
        if not email:
            return None
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT data FROM portfolios WHERE email=? AND name=?", (email, name))
            row = c.fetchone()
        if not row:
            return None
        try:
            data = json.loads(row[0])
            return PortfolioTracker.from_dict(data)
        except Exception:
            return PortfolioTracker(name)

    def list_portfolios(self, email):
        """Return portfolio names for a user; safe if email is None."""
        if not email:
            return []
        self._init_db()  # make sure table exists
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM portfolios WHERE email=? ORDER BY name", (email,))
            rows = c.fetchall()
        return [r[0] for r in rows]
