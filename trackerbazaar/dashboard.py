# dashboard.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_dashboard(selected_portfolio: str, user_email: str):
    """Modern portfolio dashboard with KPIs and charts."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"📊 Portfolio Dashboard — {selected_portfolio}")

    if not tracker.holdings:
        st.info("No holdings yet. Add transactions to see your dashboard.")
        return

    # ---- KPIs ----
    total_invested = tracker.get_total_invested()
    current_value = tracker.get_current_value()
    profit_loss = current_value - total_invested
    cagr = tracker.calculate_cagr()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💸 Total Invested", f"PKR {total_invested:,.0f}")
    col2.metric("📈 Current Value", f"PKR {current_value:,.0f}")
    col3.metric("💹 P/L", f"PKR {profit_loss:,.0f}", 
                delta=f"{(profit_loss/total_invested*100):.2f}%")
    col4.metric("📊 CAGR", f"{cagr:.2f}%")

    st.divider()

    # ---- Holdings Table ----
    st.subheader("📑 Current Holdings")
    df = pd.DataFrame(tracker.holdings)
    st.dataframe(df, use_container_width=True)

    # ---- Charts ----
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Allocation by Stock")
        alloc = df.groupby("stock")["current_value"].sum().reset_index()
        st.bar_chart(alloc.set_index("stock"))

    with col2:
        st.subheader("Profit/Loss by Stock")
        pl = df.groupby("stock")["profit_loss"].sum().reset_index()
        st.bar_chart(pl.set_index("stock"))

    # ---- Expandable Sections ----
    with st.expander("📥 Transactions"):
        if tracker.transactions:
            tx_df = pd.DataFrame(tracker.transactions)
            st.dataframe(tx_df, use_container_width=True)
        else:
            st.info("No transactions yet.")

    with st.expander("💰 Dividends"):
        if tracker.dividends:
            div_df = pd.DataFrame(tracker.dividends)
            st.dataframe(div_df, use_container_width=True)
        else:
            st.info("No dividends yet.")

    with st.expander("🏦 Cash Ledger"):
        if tracker.cash_ledger:
            cash_df = pd.DataFrame(tracker.cash_ledger)
            st.dataframe(cash_df, use_container_width=True)
        else:
            st.info("No cash transactions recorded.")
