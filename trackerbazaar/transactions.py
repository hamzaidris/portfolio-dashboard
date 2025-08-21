# transactions.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_transactions(selected_portfolio: str, user_email: str):
    """Transaction history with modern UI"""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.title("🧾 Transactions")

    if not tracker.transactions:
        st.info("No transactions yet. Add buy/sell records to see history here.")
        return

    # ---- Convert to DataFrame ----
    tx_df = pd.DataFrame(tracker.transactions).rename(columns={
        "date": "Date",
        "symbol": "Symbol",
        "type": "Type",
        "shares": "Shares",
        "price": "Price",
        "fees": "Brokerage Fee",
        "total": "Total Amount"
    })

    # ---- Sorting ----
    tx_df["Date"] = pd.to_datetime(tx_df["Date"])
    tx_df = tx_df.sort_values("Date", ascending=False)

    # ---- Summary ----
    total_buys = tx_df.loc[tx_df["Type"] == "buy", "Total Amount"].sum()
    total_sells = tx_df.loc[tx_df["Type"] == "sell", "Total Amount"].sum()
    net_cashflow = total_sells - total_buys

    col1, col2, col3 = st.columns(3)
    col1.metric("📥 Total Buys", f"{total_buys:,.2f} PKR")
    col2.metric("📤 Total Sells", f"{total_sells:,.2f} PKR")
    col3.metric("💸 Net Cashflow", f"{net_cashflow:,.2f} PKR")

    st.divider()

    # ---- Table ----
    st.subheader("📑 Transaction History")
    st.dataframe(tx_df, use_container_width=True)

    # ---- Chart ----
    st.subheader("📊 Buy vs Sell Trend")
    trend_df = tx_df.groupby(["Date", "Type"])["Total Amount"].sum().unstack(fill_value=0)
    st.line_chart(trend_df)
