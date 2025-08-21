import streamlit as st
import pandas as pd

def render_current_prices(tracker):
    st.header("💹 Current Prices")
    rows = []
    for sym, info in (tracker.current_prices or {}).items():
        rows.append({
            "Symbol": sym, "Price": info.get("price"),
            "Shariah": info.get("sharia"),
            "Change": info.get("change"),
            "Change%": info.get("changePercent"),
        })
    if rows:
        st.dataframe(pd.DataFrame(rows).sort_values("Symbol"))
    else:
        st.info("No prices loaded.")
