import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager


def show_transactions_ui(current_user):
    st.title("📜 Transactions History")

    if not current_user:
        st.warning("Please log in to view transactions.")
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

    transactions = tracker.get_transactions()
    if not transactions:
        st.info("No transactions found in this portfolio.")
        return

    # ---- Convert to DataFrame ----
    df = pd.DataFrame(transactions)

    # ---- Filter by ticker ----
    tickers = ["All"] + sorted(df["ticker"].unique().tolist())
    filter_ticker = st.selectbox("Filter by Stock", tickers)

    if filter_ticker != "All":
        df = df[df["ticker"] == filter_ticker]

    st.markdown("### Transaction Records")
    st.dataframe(df, use_container_width=True)

    # ---- Download CSV ----
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download as CSV", csv, f"{selected_portfolio}_transactions.csv", "text/csv")
