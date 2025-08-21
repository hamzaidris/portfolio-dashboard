import sqlite3, json
from .tracker import PortfolioTracker

DB = "trackerbazaar.db"

def _init_portfolios():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            data TEXT NOT NULL,
            PRIMARY KEY(email, name)
        )
        """)
        conn.commit()

class PortfolioManager:
    def __init__(self):
        _init_portfolios()

    def create_portfolio(self, name: str, email: str):
        if not (name and email):
            return None
        tracker = PortfolioTracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name: str, email: str, tracker: PortfolioTracker):
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("REPLACE INTO portfolios(email, name, data) VALUES(?,?,?)", (email, name, json.dumps(tracker.to_dict())))
            conn.commit()

    def load_portfolio(self, name: str, email: str):
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT data FROM portfolios WHERE email=? AND name=?", (email, name))
            row = c.fetchone()
        if not row:
            return None
        try:
            data = json.loads(row[0])
        except Exception:
            data = {}
        return PortfolioTracker.from_dict(data)

    def list_portfolios(self, email: str):
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM portfolios WHERE email=? ORDER BY name", (email,))
            return [r[0] for r in c.fetchall()]

    def select_portfolio(self, email: str, name: str = None):
        if name:
            return self.load_portfolio(name, email)
        names = self.list_portfolios(email)
        if names:
            return self.load_portfolio(names[0], email)
        return None
