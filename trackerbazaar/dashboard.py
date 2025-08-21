# trackerbazaar/dashboard.py

import streamlit as st
import pandas as pd
from trackerbazaar.tracker import PortfolioTracker   # ✅ correct import


def dashboard_ui():
    """Streamlit dashboard UI for portfolios."""
    st.header("📊 Portfolio Dashboard")

    tracker = PortfolioTracker()

    portfolios = tracker.get_all_portfolios()

    if not portfolios:
        st.info("No portfolios found. Please create one first.")
        return

    selected_portfolio = st.selectbox(
        "Select a Portfolio", [p["name"] for p in portfolios]
    )

    if selected_portfolio:
        portfolio_data = tracker.get_portfolio_summary(selected_portfolio)

        st.subheader(f"Summary for {selected_portfolio}")
        st.metric("Total Value", f"{portfolio_data['total_value']:.2f}")
        st.metric("Cash Balance", f"{portfolio_data['cash']:.2f}")
        st.metric("Invested Amount", f"{portfolio_data['invested']:.2f}")

        st.subheader("Holdings")
        holdings_df = pd.DataFrame(portfolio_data["holdings"])
        st.dataframe(holdings_df)
