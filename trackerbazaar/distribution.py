import sqlite3

DB_FILE = "trackerbazaar_v2.db"  # ✅ new DB

def init_distribution_table():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                portfolio_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()

def add_distribution(email, portfolio_name, ticker, amount, timestamp):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO distributions (email, portfolio_name, ticker, amount, timestamp) VALUES (?,?,?,?,?)",
            (email, portfolio_name, ticker, amount, timestamp)
        )
        conn.commit()

def get_distributions(email, portfolio_name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT ticker, amount, timestamp FROM distributions WHERE email=? AND portfolio_name=? ORDER BY id DESC",
            (email, portfolio_name)
        )
        return c.fetchall()

# Initialize
init_distribution_table()
