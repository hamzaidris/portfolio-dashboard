# trackerbazaar/tracker.py

import sqlite3
import pandas as pd
from trackerbazaar.data import DB_FILE


class PortfolioTracker:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize tables if they don't exist"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER NOT NULL,
                    ticker TEXT NOT NULL,
                    type TEXT NOT NULL, -- buy/sell
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY(portfolio_id) REFERENCES portfolios(id)
                )
            """)
            conn.commit()

    # -----------------------
    # Portfolio Management
    # -----------------------
    def create_portfolio(self, name: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO portfolios (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid

    def list_portfolios(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM portfolios")
            return cursor.fetchall()

    # -----------------------
    # Transaction Management
    # -----------------------
    def add_transaction(self, portfolio_id: int, ticker: str, type_: str,
                        quantity: float, price: float, date: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (portfolio_id, ticker, type, quantity, price, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (portfolio_id, ticker, type_, quantity, price, date))
            conn.commit()

    def get_transactions(self, portfolio_id: int):
        with self._connect() as conn:
            query = "SELECT id, ticker, type, quantity, price, date FROM transactions WHERE portfolio_id=?"
            return pd.read_sql(query, conn, params=(portfolio_id,))

    # -----------------------
    # Portfolio Summary
    # -----------------------
    def get_portfolio_summary(self, portfolio_id: int):
        """Return invested amount, current value, PnL and holdings dataframe"""
        df = self.get_transactions(portfolio_id)
        if df.empty:
            return {
                "invested": 0,
                "current_value": 0,
                "pnl": 0,
                "holdings": pd.DataFrame()
            }

        # Group by ticker
        holdings = []
        for ticker, group in df.groupby("ticker"):
            buys = group[group["type"].str.lower() == "buy"]
            sells = group[group["type"].str.lower() == "sell"]

            qty_bought = buys["quantity"].sum()
            cost = (buys["quantity"] * buys["price"]).sum()

            qty_sold = sells["quantity"].sum()
            proceeds = (sells["quantity"] * sells["price"]).sum()

            net_qty = qty_bought - qty_sold
            net_invested = cost - proceeds

            # Placeholder: assume current price = last trade price
            last_price = group.iloc[-1]["price"]
            current_value = net_qty * last_price
            pnl = current_value - net_invested

            holdings.append({
                "Ticker": ticker,
                "Quantity": net_qty,
                "Avg Buy Price": round(cost / qty_bought, 2) if qty_bought > 0 else 0,
                "Last Price": last_price,
                "Invested": round(net_invested, 2),
                "Current Value": round(current_value, 2),
                "PnL": round(pnl, 2),
            })

        holdings_df = pd.DataFrame(holdings)
        invested = holdings_df["Invested"].sum()
        current_value = holdings_df["Current Value"].sum()
        pnl = holdings_df["PnL"].sum()

        return {
            "i
