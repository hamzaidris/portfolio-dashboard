import sqlite3
from trackerbazaar.tracker import PortfolioTracker   # ✅ fixed import
from trackerbazaar.data import DB_FILE

class PortfolioManager:
    def __init__(self):
        self.db_file = DB_FILE
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL
                )
            """)
            conn.commit()

    def create_portfolio(self, email, name):
        try:
            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO portfolios (email, name) VALUES (?, ?)",
                    (email, name),
                )
                conn.commit()
        except Exception as e:
            raise RuntimeError(f"Failed to create portfolio: {e}")

    def list_portfolios(self, email):
        try:
            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT name FROM portfolios WHERE email=? ORDER BY name",
                    (email,),
                )
                return [row[0] for row in c.fetchall()]
        except Exception as e:
            raise RuntimeError(f"Database error while loading portfolios: {e}")
