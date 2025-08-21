import streamlit as st
import pandas as pd

def render_portfolio(tracker):
    st.header("📁 Portfolio")
    rows = []
    for sym, pos in (tracker.holdings or {}).items():
        rows.append({
            "Symbol": sym,
            "Qty": pos.get("qty", 0.0),
            "Avg Price": pos.get("avg_price", 0.0),
            "Invested": pos.get("invested", 0.0),
        })
    st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Symbol","Qty","Avg Price","Invested"]))
