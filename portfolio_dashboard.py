import streamlit as st
from trackerbazaar import dashboard, portfolio, distribution, cash, stock_explorer, notifications, transactions, current_prices, add_transaction, add_dividend, broker_fees, guide
from trackerbazaar.tracker import PortfolioTracker, initialize_tracker
from datetime import datetime

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
        dashboard.render_dashboard(tracker)
    elif page == "Portfolio":
        portfolio.render_portfolio(tracker)
    elif page == "Distribution":
        distribution.render_distribution(tracker)
    elif page == "Cash":
        cash.render_cash(tracker)
    elif page == "Stock Explorer":
        stock_explorer.render_stock_explorer(tracker)
    elif page == "Notifications":
        notifications.render_notifications(tracker)
    elif page == "Transactions":
        transactions.render_transactions(tracker)
    elif page == "Current Prices":
        current_prices.render_current_prices(tracker)
    elif page == "Add Transaction":
        add_transaction.render_add_transaction(tracker)
    elif page == "Add Dividend":
        add_dividend.render_add_dividend(tracker)
    elif page == "Broker Fees":
        broker_fees.render_broker_fees(tracker)
    elif page == "Guide":
        guide.render_guide()

if __name__ == '__main__':
    main()
