import streamlit as st
import pandas as pd
import plotly.express as px
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ fixed import


def show_transactions_ui(current_user):
    st.title("💼 Portfolio Transactions")

    if not current_user:
        st.warning("Please log in to manage your transactions.")
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

    st.markdown(f"### Transactions for **{selected_portfolio}**")

    # ---- Transactions Table ----
    transactions = tracker.get_transactions()
    if transactions.empty:
        st.info("No transactions available.")
    else:
        st.dataframe(transactions, use_container_width=True)

        # ---- Chart: Buy vs Sell by Ticker ----
        if "Type" in transactions.columns and "Ticker" in transactions.columns:
            fig = px.histogram(
                transactions,
                x="Ticker",
                color="Type",
                title="Buy vs Sell Count by Stock",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

        # ---- Chart: Invested Over Time ----
        if "Date" in transactions.columns and "Amount" in transactions.columns:
            transactions["Cumulative Invested"] = transactions["Amount"].cumsum()
            fig2 = px.line(
                transactions,
                x="Date",
                y="Cumulative Invested",
                title="Cumulative Investment Over Time",
            )
            st.plotly_chart(fig2, use_container_width=True)
