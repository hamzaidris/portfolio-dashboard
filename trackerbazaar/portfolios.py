import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

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
        
        # Initialize with default values
        tracker.holdings = {}
        tracker.transactions = []
        tracker.dividends = {}
        tracker.realized_gain = 0.0
        tracker.cash = 0.0
        tracker.initial_cash = 0.0
        tracker.current_prices = {}
        tracker.target_allocations = {}
        tracker.target_investment = 410000.0
        tracker.last_div_per_share = {}
        tracker.cash_deposits = []
        tracker.alerts = []
        tracker.filer_status = 'Filer'
        tracker.broker_fees = {
            'low_price_fee': 0.03,
            'sst_low_price': 0.0045,
            'brokerage_rate': 0.0015,
            'sst_rate': 0.15
        }
        
        # Save the new portfolio
        self.save_portfolio(portfolio_name, username, tracker)
        return tracker
    
    def save_portfolio(self, portfolio_name: str, username: str, tracker):
        """Save portfolio to file."""
        try:
            portfolio_path = self.get_portfolio_path(portfolio_name, username)
            
            # Convert datetime objects to strings for JSON serialization
            def convert_for_json(obj):
                if isinstance(obj, (datetime, pd.Timestamp)):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_for_json(item) for item in obj]
                return obj
            
            portfolio_data = {
                'holdings': convert_for_json(tracker.holdings),
                'transactions': convert_for_json(tracker.transactions),
                'dividends': convert_for_json(tracker.dividends),
                'realized_gain': tracker.realized_gain,
                'cash': tracker.cash,
                'initial_cash': tracker.initial_cash,
                'current_prices': convert_for_json(tracker.current_prices),
                'target_allocations': convert_for_json(tracker.target_allocations),
                'target_investment': tracker.target_investment,
                'last_div_per_share': convert_for_json(tracker.last_div_per_share),
                'cash_deposits': convert_for_json(tracker.cash_deposits),
                'alerts': convert_for_json(tracker.alerts),
                'filer_status': tracker.filer_status,
                'broker_fees': tracker.broker_fees
            }
            
            with open(portfolio_path, 'w') as f:
                json.dump(portfolio_data, f, indent=2)
                
            st.sidebar.success(f"Portfolio '{portfolio_name}' saved!")
            
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
                
                tracker = PortfolioTracker()
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
    
    def delete_portfolio(self, portfolio_name: str, username: str):
        """Delete a portfolio."""
        try:
            portfolio_path = self.get_portfolio_path(portfolio_name, username)
            if os.path.exists(portfolio_path):
                os.remove(portfolio_path)
                st.success(f"Portfolio '{portfolio_name}' deleted!")
                return True
        except Exception as e:
            st.error(f"Error deleting portfolio: {e}")
        return False
