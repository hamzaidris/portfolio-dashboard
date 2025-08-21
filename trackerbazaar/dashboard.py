import streamlit as st
import pandas as pd

def render_dashboard(tracker):
    st.header("📊 Dashboard")
    mv = tracker.market_value()
    invested = tracker.total_invested()
    cash = tracker.cash
    total = mv + cash
    pnl = (mv - invested)
    st.metric("Market Value", f"{mv:,.2f} PKR")
    st.metric("Cash", f"{cash:,.2f} PKR")
    st.metric("Total Portfolio", f"{total:,.2f} PKR")
    st.metric("Unrealized P/L", f"{pnl:,.2f} PKR")

    rows = []
    for sym, pos in (tracker.holdings or {}).items():
        price = (tracker.current_prices.get(sym, {}) or {}).get("price", pos.get("avg_price", 0.0))
        rows.append({
            "Symbol": sym,
            "Qty": pos.get("qty", 0.0),
            "Avg Price": pos.get("avg_price", 0.0),
            "Last Price": price,
            "Market Value": price * pos.get("qty", 0.0),
        })
    if rows:
        st.subheader("Holdings")
        st.dataframe(pd.DataFrame(rows))
    else:
        st.info("No holdings yet. Add a transaction to get started.")
