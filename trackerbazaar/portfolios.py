import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioManager:
    def __init__(self):
        self.db_path = "trackerbzzar.db"  # Align with users.py
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database for portfolios."""
        try:
            # Remove old database file if it exists to avoid conflicts
            if os.path.exists("trackerbazaar.db"):
                logger.warning("Old database 'trackerbazaar.db' found and will be ignored. Using 'trackerbzzar.db'.")
                os.remove("trackerbazaar.db")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create portfolios table with necessary columns
                logger.info("Creating portfolios table in trackerbzzar.db.")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolios (
                        portfolio_name TEXT PRIMARY KEY,
                        user_email TEXT NOT NULL,
                        data TEXT,  -- Store portfolio data as JSON or similar
                        FOREIGN KEY (user_email) REFERENCES users(email)
                    )
                """)

                conn.commit()
                logger.info("Portfolios table initialization completed.")
        except sqlite3.OperationalError as e:
            logger.error(f"Failed to initialize portfolios database: {e}")
            raise  # Re-raise to be caught by the calling code
        except Exception as e:
            logger.error(f"Unexpected error initializing portfolios database: {e}")
            raise  # Re-raise to be caught by the calling code

    def create_portfolio(self, portfolio_name, user_email):
        """Create a new portfolio for the given user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO portfolios (portfolio_name, user_email, data)
                    VALUES (?, ?, ?)
                """, (portfolio_name, user_email, "{}"))  # Initialize with empty data
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            logger.error(f"Portfolio {portfolio_name} already exists for user {user_email}")
            return False
        except sqlite3.OperationalError as e:
            logger.error(f"Database error creating portfolio: {e}")
            return False

    def select_portfolio(self, user_email):
        """Select a portfolio for the given user (implementation depends on your logic)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT portfolio_name, data FROM portfolios WHERE user_email = ?", (user_email,))
                result = cursor.fetchone()
                if result:
                    portfolio_name, data = result
                    # Assuming data is a JSON string, parse it or return as needed
                    return {"name": portfolio_name, "data": data}
                return None
        except sqlite3.OperationalError as e:
            logger.error(f"Database error selecting portfolio: {e}")
            return None

    def save_portfolio(self, portfolio_name, user_email, tracker):
        """Save portfolio data for the given user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Convert tracker to a string (e.g., JSON) for storage
                data = str(tracker)  # Adjust based on your tracker object
                cursor.execute("""
                    UPDATE portfolios SET data = ? WHERE portfolio_name = ? AND user_email = ?
                """, (data, portfolio_name, user_email))
                conn.commit()
                if cursor.rowcount == 0:
                    cursor.execute("""
                        INSERT INTO portfolios (portfolio_name, user_email, data)
                        VALUES (?, ?, ?)
                    """, (portfolio_name, user_email, data))
                    conn.commit()
                return True
        except sqlite3.OperationalError as e:
            logger.error(f"Database error saving portfolio: {e}")
            return False