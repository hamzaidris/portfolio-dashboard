import streamlit as st
import sqlite3
import json
from trackerbazaar.tracker import PortfolioTracker

class PortfolioManager:
    def __init__(self):
        self.db_path = "trackerbazaar.db"
        self._init_db()
        if "portfolio_manager" not in st.session_state:
            st.session_state.portfolio_manager = self
        if "portfolios" not in st.session_state:
            st.session_state.portfolios = {}

    def _init_db(self):
        """Initialize SQLite database with portfolios table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    email TEXT,
                    portfolio_name TEXT,
                    portfolio_data TEXT,
                    PRIMARY KEY (email, portfolio_name)
                )
            """)
            conn.commit()

    def create_portfolio(self, name, email):
        """Create a new portfolio for the user and save to database."""
        if not email:
            return None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT portfolio_name FROM portfolios WHERE email = ? AND portfolio_name = ?", (email, name))
            if cursor.fetchone():
                return None
            tracker = PortfolioTracker()
            portfolio_data = json.dumps({
                'transactions': tracker.transactions,
                'holdings': tracker.holdings,
                'dividends': tracker.dividends,
                'realized_gain': tracker.realized_gain,
                'cash': tracker.cash,
                'initial_cash': tracker.initial_cash,
                'current_prices': tracker.current_prices,
                'target_allocations': tracker.target_allocations,
                'target_investment': tracker.target_investment,
                'last_div_per_share': tracker.last_div_per_share,
                'cash_deposits': tracker.cash_deposits,
                'alerts': tracker.alerts,
                'filer_status': tracker.filer_status,
                'broker_fees': tracker.broker_fees
            })
            cursor.execute("INSERT INTO portfolios (email, portfolio_name, portfolio_data) VALUES (?, ?, ?)", (email, name, portfolio_data))
            conn.commit()
            st.session_state.portfolios[name] = tracker
            return tracker

    def get_portfolio(self, name, email):
        """Retrieve a portfolio for the user from the database."""
        if not email or not name:
            return None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT portfolio_data FROM portfolios WHERE email = ? AND portfolio_name = ?", (email, name))
            result = cursor.fetchone()
            if result:
                tracker = PortfolioTracker()
                data = json.loads(result[0])
                tracker.transactions = data.get('transactions', [])
                tracker.holdings = data.get('holdings', {})
                tracker.dividends = data.get('dividends', {})
                tracker.realized_gain = data.get('realized_gain', 0.0)
                tracker.cash = data.get('cash', 0.0)
                tracker.initial_cash = data.get('initial_cash', 0.0)
                tracker.current_prices = data.get('current_prices', {})
                tracker.target_allocations = data.get('target_allocations', {})
                tracker.target_investment = data.get('target_investment', 410000.0)
                tracker.last_div_per_share = data.get('last_div_per_share', {})
                tracker.cash_deposits = data.get('cash_deposits', [])
                tracker.alerts = data.get('alerts', [])
                tracker.filer_status = data.get('filer_status', 'Filer')
                tracker.broker_fees = data.get('broker_fees', {
                    'low_price_fee': 0.03,
                    'sst_low_price': 0.0045,
                    'brokerage_rate': 0.0015,
                    'sst_rate': 0.15
                })
                return tracker
        return None

    def get_portfolio_names(self, email):
        """Get all portfolio names for the user."""
        if not email:
            return []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT portfolio_name FROM portfolios WHERE email = ?", (email,))
            return [row[0] for row in cursor.fetchall()]

    def select_portfolio(self, email):
        """Render portfolio selection dropdown."""
        if not email:
            st.warning("Please log in to select a portfolio.")
            return None
        portfolio_names = self.get_portfolio_names(email)
        if not portfolio_names:
            st.warning("No portfolios created. Create one first.")
            return None
        selected = st.sidebar.selectbox("Select Portfolio", portfolio_names, key="selected_portfolio")
        if selected:
            tracker = self.get_portfolio(selected, email)
            if tracker:
                st.session_state.portfolios[selected] = tracker
                return tracker
        return None

    def save_portfolio(self, name, email, tracker):
        """Save the portfolio to the database."""
        if not email or not name:
            return
        portfolio_data = json.dumps({
            'transactions': tracker.transactions,
            'holdings': tracker.holdings,
            'dividends': tracker.dividends,
            'realized_gain': tracker.realized_gain,
            'cash': tracker.cash,
            'initial_cash': tracker.initial_cash,
            'current_prices': tracker.current_prices,
            'target_allocations': tracker.target_allocations,
            'target_investment': tracker.target_investment,
            'last_div_per_share': tracker.last_div_per_share,
            'cash_deposits': tracker.cash_deposits,
            'alerts': tracker.alerts,
            'filer_status': tracker.filer_status,
            'broker_fees': tracker.broker_fees
        })
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO portfolios (email, portfolio_name, portfolio_data)
                VALUES (?, ?, ?)
            """, (email, name, portfolio_data))
            conn.commit()
