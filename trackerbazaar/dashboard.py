# trackerbazaar/dashboard.py
import streamlit as st
from trackerbazaar.portfolio_tracker import PortfolioTracker

def run():
    st.title("📊 Portfolio Dashboard")

    tracker = PortfolioTracker()

    # List all portfolios
    portfolios = tracker.list_portfolios()

    if not portfolios:
        st.info("No portfolios yet. Please add one from 'Add Transaction'.")
        return

    for pid, name in portfolios:
        st.subheader(f"Portfolio: {name}")

        try:
            # Fetch portfolio summary (you may need to extend PortfolioTracker with this)
            summary = tracker.get_portfolio_summary(pid)

            # Display summary in a nice layout
            st.metric("Total Invested", f"{summary['invested']:,} PKR")
            st.metric("Current Value", f"{summary['current_value']:,} PKR")
            st.metric("Profit / Loss", f"{summary['pnl']:,} PKR")

            st.write("### Holdings")
            st.dataframe(summary["holdings"])

        except Exception as e:
            st.error(f"Could not load summary for {name}: {e}")
