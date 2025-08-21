import sqlite3
import json
import streamlit as st
from trackerbazaar.tracker import Tracker


class PortfolioManager:
    def __init__(self):
        self.db_path = "trackerbazaar.db"
        self._init_db()

    def _init_db(self):
        """Ensure portfolios table exists with required schema"""
        with sqlite3.connect(self.db_path) as conn:
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

    def create_portfolio(self, name, email):
        tracker = Tracker()
        self.save_portfolio(name, email, tracker)
        return tracker

    def save_portfolio(self, name, email, tracker):
        """Save or update portfolio"""
        tracker_data = json.dumps(tracker.to_dict())
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO portfolios (email, name, data)
                VALUES (?,?,?)
                ON CONFLICT(email, name) DO UPDATE SET data=excluded.data
                """,
                (email, name, tracker_data),
            )
            conn.commit()

    def load_portfolio(self, name, email):
        """Load portfolio by name"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT data FROM portfolios WHERE email=? AND name=?",
                (email, name),
            )
            row = c.fetchone()
            if row:
                return Tracker.from_dict(json.loads(row[0]))
            else:
                raise ValueError("Portfolio not found.")

    def list_portfolios(self, email):
        """Return list of portfolio names for given email"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM portfolios WHERE email=? ORDER BY name", (email,))
            rows = c.fetchall()
            return [r[0] for r in rows] if rows else []
