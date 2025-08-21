import streamlit as st
from datetime import date

def render_add_transaction(tracker):
    st.header("➕ Add Transaction")
    with st.form("add_txn"):
        d = st.date_input("Date", value=date.today())
        sym = st.text_input("Symbol").upper().strip()
        side = st.selectbox("Side", ["buy", "sell"])
        qty = st.number_input("Quantity", min_value=0.0, step=1.0)
        price = st.number_input("Price", min_value=0.0, step=0.05)
        fee = st.number_input("Fee (optional)", min_value=0.0, step=1.0, value=0.0)
        ok = st.form_submit_button("Add")
    if ok:
        if not sym or qty <= 0 or price <= 0:
            st.error("Provide valid symbol, qty, and price.")
        else:
            tracker.add_transaction(d.isoformat(), sym, side, qty, price, fee)
            st.success(f"Added {side} {qty} {sym} @ {price}")

def render_sample_distribution(tracker):
    st.caption("Tip: Use 'Distribution' tab to set targets (placeholder).")
