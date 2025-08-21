import streamlit as st
from datetime import date

def render_add_dividend(tracker):
    st.header("🏦 Add Dividend")
    with st.form("add_div"):
        d = st.date_input("Date", value=date.today())
        sym = st.text_input("Symbol").upper().strip()
        amt = st.number_input("Amount", min_value=0.0, step=1.0)
        ok = st.form_submit_button("Add Dividend")
    if ok:
        if not sym or amt <= 0:
            st.error("Provide valid symbol and amount.")
        else:
            tracker.add_dividend(d.isoformat(), sym, amt)
            st.success(f"Added dividend {amt} for {sym}")
