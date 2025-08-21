import sqlite3

DB_FILE = "trackerbazaar_v2.db"  # ✅ new DB

def get_portfolio_summary(email, portfolio_name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()

        # Total invested
        c.execute("SELECT SUM(quantity * price) FROM transactions WHERE email=? AND portfolio_name=? AND type='buy'",
                  (email, portfolio_name))
        invested = c.fetchone()[0] or 0

        # Total returns (sell + dividends)
        c.execute("SELECT SUM(quantity * price) FROM transactions WHERE email=? AND portfolio_name=? AND type='sell'",
                  (email, portfolio_name))
        realized = c.fetchone()[0] or 0

        c.execute("SELECT SUM(amount) FROM dividends WHERE email=? AND portfolio_name=?",
                  (email, portfolio_name))
        dividends = c.fetchone()[0] or 0

        return {
            "invested": invested,
            "realized": realized,
            "dividends": dividends,
            "net": realized + dividends - invested
        }
