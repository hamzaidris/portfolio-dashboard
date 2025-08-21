import streamlit as st
import pandas as pd

def render_stock_explorer(tracker):
    st.header("🔎 Stock Explorer")
    q = st.text_input("Search symbol")
    if q:
        q = q.upper()
        rows = []
        for sym, info in (tracker.current_prices or {}).items():
            if q in sym:
                rows.append({
                    "Symbol": sym, "Price": info.get("price"), "Shariah": info.get("sharia"),
                    "Change": info.get("change"), "Change%": info.get("changePercent")
                })
        st.dataframe(pd.DataFrame(rows))
    else:
        st.info("Enter a symbol fragment to search prices.")
