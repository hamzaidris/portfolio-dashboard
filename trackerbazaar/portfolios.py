import streamlit as st
import json
import os

class PortfolioManager:
    def __init__(self):
        self.portfolios_dir = "portfolios"
        os.makedirs(self.portfolios_dir, exist_ok=True)
    
    def get_portfolio_path(self, portfolio_name: str, username: str) -> str:
        """Get file path for portfolio."""
        return os.path.join(self.portfolios_dir, f"{username}_{portfolio_name}.json")
    
    def create_portfolio(self, portfolio_name: str, username: str):
        """Create a new portfolio."""
        from trackerbazaar.tracker import PortfolioTracker
        tracker = PortfolioTracker()  # No username parameter
        self.save_portfolio(portfolio_name, username, tracker)
        return tracker
    
    def save_portfolio(self, portfolio_name: str, username: str, tracker):
        """Save portfolio to file."""
        try:
            portfolio_path = self.get_portfolio_path(portfolio_name, username)
            with open(portfolio_path, 'w') as f:
                json.dump({
                    'holdings': tracker.holdings,
                    'transactions': tracker.transactions,
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
                }, f, default=str)
        except Exception as e:
            st.error(f"Error saving portfolio: {e}")
    
    def load_portfolio(self, portfolio_name: str, username: str):
        """Load portfolio from file."""
        from trackerbazaar.tracker import PortfolioTracker
        try:
            portfolio_path = self.get_portfolio_path(portfolio_name, username)
            if os.path.exists(portfolio_path):
                with open(portfolio_path, 'r') as f:
                    data = json.load(f)
                tracker = PortfolioTracker()  # No username parameter
                tracker.holdings = data.get('holdings', {})
                tracker.transactions = data.get('transactions', [])
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
        except Exception as e:
            st.error(f"Error loading portfolio: {e}")
        return None
    
    def select_portfolio(self, username: str):
        """Select portfolio from available options."""
        if 'selected_portfolio' not in st.session_state:
            st.session_state.selected_portfolio = None
        
        # Get available portfolios
        available_portfolios = []
        for file in os.listdir(self.portfolios_dir):
            if file.startswith(f"{username}_") and file.endswith(".json"):
                portfolio_name = file[len(username) + 1:-5]  # Remove username_ and .json
                available_portfolios.append(portfolio_name)
        
        if available_portfolios:
            selected = st.sidebar.selectbox(
                "Select Portfolio",
                available_portfolios,
                index=0 if not st.session_state.selected_portfolio else available_portfolios.index(st.session_state.selected_portfolio)
            )
            
            if selected != st.session_state.selected_portfolio:
                st.session_state.selected_portfolio = selected
                st.rerun()
            
            return self.load_portfolio(selected, username)
        
        return None
