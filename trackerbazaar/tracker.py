# trackerbazaar/tracker.py

import sqlite3
from trackerbazaar.data import DB_FILE, TABLES

class PortfolioTracker:
    def __init__(self):
        self.db_path = DB_FILE

    def list_portfolios(self, owner_email=None):
        """
        Return all portfolios. If owner_email is provided,
        only return portfolios belonging to that user.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if owner_email:
                cursor.execute(
                    f"SELECT id, name FROM {TABLES['portfolios']} WHERE owner_email=?",
                    (owner_email,)
                )
            else:
                cursor.execute(f"SELECT id, name FROM {TABLES['portfolios']}")
            return cursor.fetchall()

    def create_portfolio(self, name, owner_email):
        """
        Create a new portfolio for a given owner.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {TABLES['portfolios']} (name, owner_email) VALUES (?, ?)",
                (name, owner_email)
            )
            conn.commit()
            return cursor.lastrowid

    def delete_portfolio(self, portfolio_id):
        """
        Delete a portfolio by its ID.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {TABLES['portfolios']} WHERE id=?",
                (portfolio_id,)
            )
            conn.commit()
