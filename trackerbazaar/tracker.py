# trackerbazaar/tracker.py

import sqlite3
from datetime import datetime

DB_FILE = "trackerbazaar_v2.db"


class PortfolioTracker:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        """Initialize the database schema for portfolios, transactions, and dividends."""
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()

            # Portfolios table
            c.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Transactions table
            c.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    transaction_type TEXT NOT NULL, -- BUY or SELL
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    brokerage REAL DEFAULT 0,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
                )
            """)

            # Dividends table
            c.execute("""
                CREATE TABLE IF NOT EXISTS dividends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
                )
            """)

            conn.commit()

    # ---------------- Portfolio ----------------

    def create_portfolio(self, email: str, name: str):
        """Create a new portfolio."""
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO portfolios (email, name) VALUES (?, ?)",
                (email, name),
            )
            conn.commit()

    def list_portfolios(self, email: str):
        """List all portfolios for a given user."""
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM portfolios WHERE email=? ORDER BY name", (email,))
            return c.fetchall()

    # ---------------- Transactions ----------------

    def add_transaction(self, portfolio_id: int, date: str, ticker: str,
                        transaction_type: str, quantity: float, price: float, brokerage: float = 0.0):
        """Add a buy or sell transaction."""
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO transactions (portfolio_id, date, ticker, transaction_type, quantity, price, brokerage)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (portfolio_id, date, ticker, transaction_type.upper(), quantity, price, brokerage),
            )
            conn.commit()

    def get_transactions(self, portfolio_id: int):
        """Get all transactions for a portfolio."""
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT date, ticker, transaction_type, quantity, price, brokerage "
                "FROM transactions WHERE portfolio_id=? ORDER BY date",
                (portfolio_id,),
            )
            return c.fetchall()

    # ---------------- Dividends ----------------

    def add_dividend(self, portfolio_id: int, date: str, ticker: str, amount: float):
        """Record a dividend payment."""
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO dividends (portfolio_id, date, ticker, amount) VALUES (?, ?, ?, ?)",
                (portfolio_id, date, ticker, amount),
            )
            conn.commit()

    def get_dividends(self, portfolio_id: int):
        """Get all dividends for a portfolio."""
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT date, ticker, amount FROM dividends WHERE portfolio_id=? ORDER BY date",
                (portfolio_id,),
            )
            return c.fetchall()

    # ---------------- Metrics ----------------

    def calculate_portfolio_value(self, portfolio_id: int, current_prices: dict):
        """
        Calculate current portfolio value using latest prices.
        current_prices: dict { 'TICKER': price }
        """
        holdings = {}
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT ticker, transaction_type, quantity, price FROM transactions WHERE portfolio_id=?",
                (portfolio_id,),
            )
            for ticker, tx_type, qty, price in c.fetchall():
                if ticker not in holdings:
                    holdings[ticker] = 0
                if tx_type == "BUY":
                    holdings[ticker] += qty
                elif tx_type == "SELL":
                    holdings[ticker] -= qty

        total_value = 0
        for ticker, qty in holdings.items():
            if ticker in current_prices:
                total_value += qty * current_prices[ticker]

        return total_value
