# trackerbazaar/dashboard.py
import streamlit as st
from trackerbazaar.tracker import PortfolioTracker   # ✅ fixed import

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
            # Fetch portfolio summary (requires PortfolioTracker.get_portfolio_summary)
            summary = tracker.get_portfolio_summary(pid)

            # Display summary in a nice layout
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invested", f"{summary['invested']:,} PKR")
            col2.metric("Current Value", f"{summary['current_value']:,} PKR")
            col3.metric("Profit / Loss", f"{summary['pnl']:,} PKR")

            st.write("### Holdings")
            st.dataframe(summary["holdings"])

        except Exception as e:
            st.error(f"Could not load summary for {name}: {e}")
