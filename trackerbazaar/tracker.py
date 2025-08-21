# trackerbazaar/tracker.py

import sqlite3
from trackerbazaar.data import DB_FILE

class PortfolioTracker:
    """Basic tracker stub — extend as needed."""

    def __init__(self):
        self.db_path = DB_FILE
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def list_portfolios(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, created_at FROM portfolios")
            return cursor.fetchall()
