# trackerbazaar/data.py
"""
Centralized configuration and constants for TrackerBazaar.
This ensures consistent references across all modules.
"""

import os

# Database file (consistent for v2)
DB_FILE = os.path.join(os.path.dirname(__file__), "trackerbazaar_v2.db")

# Default currency
DEFAULT_CURRENCY = "PKR"

# Table names (to avoid typos)
TABLES = {
    "users": "users",
    "portfolios": "portfolios",
    "transactions": "transactions",
    "dividends": "dividends",
    "cash": "cash",
}

# SQL schema definitions
SCHEMA = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """,
    "portfolios": """
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            owner_email TEXT NOT NULL,
            FOREIGN KEY (owner_email) REFERENCES users(email)
        )
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            ticker TEXT NOT NULL,
            type TEXT CHECK(type IN ('BUY','SELL')) NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        )
    """,
    "dividends": """
        CREATE TABLE IF NOT EXISTS dividends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            ticker TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        )
    """,
    "cash": """
        CREATE TABLE IF NOT EXISTS cash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            amount REAL NOT NULL,
            type TEXT CHECK(type IN ('DEPOSIT','WITHDRAW')) NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        )
    """,
}
