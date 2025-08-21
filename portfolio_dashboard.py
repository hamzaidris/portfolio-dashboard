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
from trackerbazaar.add_transaction import render_add_transaction, render_sample_distribution
from trackerbazaar.add_dividend import render_add_dividend
from trackerbazaar.broker_fees import render_broker_fees
from trackerbazaar.guide import render_guide
from trackerbazaar.tracker import PortfolioTracker, initialize_tracker
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager
from datetime import datetime

# Add parent directory to sys.path for package resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    st.set_page_config(page_title="TrackerBazaar - Portfolio Dashboard", layout="wide")
    st.title("📈 TrackerBazaar - Portfolio Dashboard")
    st.markdown("A portfolio management platform for tracking and optimizing your investments across stocks, mutual funds, and commodities. Stay ahead with real-time insights and analytics.")

    user_manager = UserManager()
    portfolio_manager = PortfolioManager()

    # Handle login state
    if not user_manager.is_logged_in():
        tabs = st.tabs(["Login", "Sign Up"])
        with tabs[0]:
            user_manager.login()
        with tabs[1]:
            user_manager.signup()
        st.info("Please log in or sign up to access your portfolios.")
        return

    # Show logout button in sidebar for logged-in users
    st.sidebar.header("User")
    user_manager.logout()

    # Initialize session state
    if 'portfolios' not in st.session_state:
        st.session_state.portfolios = {}
    if 'selected_portfolio' not in st.session_state:
        st.session_state.selected_portfolio = None

    # Portfolio creation - FIXED: PortfolioTracker doesn't take username parameter
    st.sidebar.header("Portfolio Management")
    new_portfolio_name = st.sidebar.text_input("New Portfolio Name", key="new_portfolio_name")
    if st.sidebar.button("Create Portfolio", key="create_portfolio"):
        tracker = PortfolioTracker()  # REMOVED username parameter
        if tracker:
            st.session_state.portfolios[new_portfolio_name] = tracker
            st.session_state.selected_portfolio = new_portfolio_name
            st.success(f"Portfolio '{new_portfolio_name}' created successfully!")
            st.rerun()

    # Portfolio selection
    tracker = portfolio_manager.select_portfolio(user_manager.get_current_user())
    if not tracker:
        st.info("No portfolio selected. Create or select a portfolio.")
        return

    # Initialize tracker if not already initialized
    if not tracker.current_prices:
        initialize_tracker(tracker)
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, user_manager.get_current_user(), tracker)

    st.sidebar.header("Tax Settings")
    filer_status = st.sidebar.selectbox("Filer Status", ["Filer", "Non-Filer"], index=0 if tracker.filer_status == 'Filer' else 1)
    if filer_status != tracker.filer_status:
        tracker.update_filer_status(filer_status)
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, user_manager.get_current_user(), tracker)
        st.session_state.data_changed = True

    if st.session_state.get('data_changed', False):
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, user_manager.get_current_user(), tracker)
        st.session_state.data_changed = False
        st.rerun()

    # Navigation
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Portfolio", "Distribution", "Cash", "Stock Explorer", "Notifications", "Transactions", "Current Prices", "Add Transaction", "Add Dividend", "Broker Fees", "Guide"])

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
        render_sample_distribution(tracker)
    elif page == "Add Dividend":
        render_add_dividend(tracker)
    elif page == "Broker Fees":
        render_broker_fees(tracker)
    elif page == "Guide":
        render_guide()

if __name__ == '__main__':
    main()
