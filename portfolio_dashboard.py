# portfolio_dashboard.py
import sys
import os
import streamlit as st
from trackerbazaar.dashboard import render_dashboard
from trackerbazaar.portfolio import render_portfolio
from trackerbazaar.distribution import render_distribution
from trackerbazaar.cash import render_cash
from trackerbazaar.stock_explorer import render_stock_explorer
from trackerbazaar.notifications import render_notifications
from trackerbazaar.transactions import render_transactions
from trackerbazaar.current_prices import render_current_prices
from trackerbazaar.add_transaction import render_add_transaction
from trackerbazaar.add_dividend import render_add_dividend
from trackerbazaar.broker_fees import render_broker_fees
from trackerbazaar.guide import render_guide
from trackerbazaar.tracker import PortfolioTracker, initialize_tracker
from datetime import datetime

# Add parent directory to sys.path for package resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Debug: Print current working directory
print("Current working directory:", os.getcwd())

def main():
    st.set_page_config(page_title="TrackerBazaar - Portfolio Dashboard", layout="wide")
    st.title("📈 TrackerBazaar - Portfolio Dashboard")
    st.markdown("A portfolio management platform for tracking and optimizing your investments across stocks, mutual funds, and commodities. Stay ahead with real-time insights and analytics.")

    if 'tracker' not in st.session_state:
        st.session_state.tracker = PortfolioTracker()
        initialize_tracker(st.session_state.tracker)
        st.session_state.update_allocations = False
        st.session_state.update_filer_status = False
        st.session_state.data_changed = False

    tracker = st.session_state.tracker

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Portfolio", "Distribution", "Cash", "Stock Explorer", "Notifications", "Transactions", "Current Prices", "Add Transaction", "Add Dividend", "Broker Fees", "Guide"])

    st.sidebar.header("Tax Settings")
    filer_status = st.sidebar.selectbox("Filer Status", ["Filer", "Non-Filer"], index=0 if tracker.filer_status == 'Filer' else 1)
    if filer_status != tracker.filer_status:
        tracker.update_filer_status(filer_status)

    if st.session_state.get('update_filer_status', False) or st.session_state.get('update_allocations', False) or st.session_state.get('data_changed', False):
        st.session_state.update_filer_status = False
        st.session_state.update_allocations = False
        st.session_state.data_changed = False
        st.rerun()

    # Call the appropriate tab function
    if page == "Dashboard":
        render_dashboard(tracker)
    elif page == "Portfolio":
        render_portfolio(tracker)
    elif page == "Distribution":
        render_distribution(tracker)
    elif page == "Cash":
        render_cash(tracker)
    elif page == "Stock Explorer":
        render_stock_explorer(tracker)
    elif page == "Notifications":
        render_notifications(tracker)
    elif page == "Transactions":
        render_transactions(tracker)
    elif page == "Current Prices":
        render_current_prices(tracker)
    elif page == "Add Transaction":
        render_add_transaction(tracker)
    elif page == "Add Dividend":
        render_add_dividend(tracker)
    elif page == "Broker Fees":
        render_broker_fees(tracker)
    elif page == "Guide":
        render_guide()

if __name__ == '__main__':
    main()
