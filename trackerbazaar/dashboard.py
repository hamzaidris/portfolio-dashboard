import streamlit as st
import plotly.express as px
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ fixed import


def show_dashboard_ui(current_user):
    st.title("📊 Portfolio Dashboard")

    if not current_user:
        st.warning("Please log in to view your dashboard.")
        return

    pm = PortfolioManager()
    portfolios = pm.list_portfolios(current_user)

    if not portfolios:
        st.info("No portfolios found. Please create one first.")
        return

    selected_portfolio = st.selectbox("Select Portfolio", portfolios)

    tracker = pm.load_portfolio(selected_portfolio, current_user)
    if not tracker:
        st.error("Failed to load portfolio.")
        return

    st.markdown(f"### Dashboard for **{selected_portfolio}**")

    # ---- Metrics ----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Invested", f"{tracker.total_invested():,.2f}")
    with col2:
        st.metric("Current Value", f"{tracker.current_value():,.2f}")
    with col3:
        st.metric("Unrealized P/L", f"{tracker.unrealized_pl():,.2f}")
    with col4:
        st.metric("Total Transactions", len(tracker.get_transactions()))

    st.divider()

    # ---- Holdings Breakdown (Pie Chart) ----
    holdings = tracker.get_holdings()
    if not holdings.empty:
        fig = px.pie(
            holdings,
            values="Current Value",
            names="Ticker",
            title="Portfolio Allocation by Stock",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No holdings available to display.")

    # ---- Performance Over Time (Line Chart) ----
    transactions = tracker.get_transactions()
    if not transactions.empty:
        transactions["Cumulative Invested"] = transactions["Amount"].cumsum()
        fig2 = px.line(
            transactions,
            x="Date",
            y="Cumulative Invested",
            title="Investment Growth Over Time",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No transactions available to plot performance.")
