import sqlite3
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "trackerbazaar.db"

def _tracker_to_dict(tracker):
    """Serialize key fields of the tracker safely for storage."""
    fields = [
        "transactions", "holdings", "dividends", "realized_gain", "cash", "initial_cash",
        "current_prices", "target_allocations", "target_investment", "last_div_per_share",
        "cash_deposits", "alerts", "filer_status", "broker_fees"
    ]
    out = {}
    for f in fields:
        out[f] = getattr(tracker, f, None)
    return out

class PortfolioManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database for portfolios."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    """CREATE TABLE IF NOT EXISTS portfolios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_email TEXT NOT NULL,
                        portfolio_name TEXT NOT NULL,
                        data TEXT NOT NULL,
                        UNIQUE(user_email, portfolio_name)
                    )"""
                )
                conn.commit()
        except sqlite3.OperationalError as e:
            logger.error(f"Database init error: {e}")

    def save_portfolio(self, portfolio_name, user_email, tracker):
        """Upsert a portfolio for a user."""
        try:
            data_json = json.dumps(_tracker_to_dict(tracker))
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    """UPDATE portfolios SET data=?
                       WHERE user_email=? AND portfolio_name=?""",
                    (data_json, user_email, portfolio_name)
                )
                if cur.rowcount == 0:
                    cur.execute(
                        """INSERT INTO portfolios(user_email, portfolio_name, data)
                           VALUES (?,?,?)""",
                        (user_email, portfolio_name, data_json)
                    )
                conn.commit()
            return True
        except sqlite3.OperationalError as e:
            logger.error(f"Database error saving portfolio: {e}")
            return False

    def get_portfolio(self, portfolio_name, user_email):
        """Return the stored portfolio JSON as a dict, or None."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    """SELECT data FROM portfolios
                       WHERE user_email=? AND portfolio_name=?""",
                    (user_email, portfolio_name)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return json.loads(row[0])
        except sqlite3.OperationalError as e:
            logger.error(f"Database error reading portfolio: {e}")
            return None

    def list_portfolios(self, user_email):
        """List portfolio names for the given user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    """SELECT portfolio_name FROM portfolios
                       WHERE user_email=? ORDER BY portfolio_name""",
                    (user_email,)
                )
                return [r[0] for r in cur.fetchall()]
        except sqlite3.OperationalError as e:
            logger.error(f"Database error listing portfolios: {e}")
            return []

    def create_portfolio(self, portfolio_name, user_email, tracker):
        """Create a new portfolio (delegates to save)."""
        return self.save_portfolio(portfolio_name, user_email, tracker)
