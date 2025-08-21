# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_dashboard(selected_portfolio: str, user_email: str):
    """Display portfolio dashboard with KPIs and charts."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"📊 Dashboard — {selected_portfolio}")

    # ---- KPIs ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"PKR {tracker.total_invested:,.0f}")
    with col2:
        st.metric("Current Value", f"PKR {tracker.current_value:,.0f}")
    with col3:
        profit_loss = tracker.current_value - tracker.total_invested
        st.metric(
            "P/L",
            f"PKR {profit_loss:,.0f}",
            delta=f"{(profit_loss / tracker.total_invested * 100):.2f}%" if tracker.total_invested > 0 else "0%",
        )

    st.divider()

    # ---- Holdings Table ----
    if not tracker.holdings:
        st.info("No holdings yet. Add transactions in the Transactions tab.")
        return

    df = pd.DataFrame(tracker.holdings)
    st.dataframe(df, use_container_width=True)

    # ---- Chart: Portfolio Allocation ----
    try:
        fig = px.pie(
            df,
            names="ticker",
            values="current_value",
            title="Portfolio Allocation",
            hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not generate allocation chart: {e}")
