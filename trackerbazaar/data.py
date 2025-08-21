# trackerbazaar/data.py
import sqlite3

# Single source of truth for the DB filename
DB_FILE = "trackerbazaar_v3.db"

# Base CREATE TABLE DDLs (new installs will have the latest schema)
TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        );
    """,
    "portfolios": """
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            owner_email TEXT NOT NULL
        );
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('BUY','SELL')),
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            fees REAL DEFAULT 0,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        );
    """,
    "dividends": """
        CREATE TABLE IF NOT EXISTS dividends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        );
    """,
    "cash": """
        CREATE TABLE IF NOT EXISTS cash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
        );
    """
}

def _has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    return column in cols

def init_db():
    """Create tables (if missing) and run lightweight migrations."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()

    # Create base tables
    for ddl in TABLES.values():
        cur.execute(ddl.strip())

    # ---- Migrations / Backward compatibility ----
    # Some older DBs might not have these columns. Add them if missing.

    # portfolios.owner_email (should exist, but ensure it)
    if not _has_column(conn, "portfolios", "owner_email"):
        cur.execute("ALTER TABLE portfolios ADD COLUMN owner_email TEXT DEFAULT ''")

    # cash.note (your current error)
    if not _has_column(conn, "cash", "note"):
        cur.execute("ALTER TABLE cash ADD COLUMN note TEXT")

    # You can add more migrations here if needed in the future.

    conn.commit()
    conn.close()
