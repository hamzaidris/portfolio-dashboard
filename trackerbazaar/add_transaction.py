import streamlit as st
from datetime import datetime
from .tracker import PortfolioTracker

def render_add_transaction(tracker):
    st.header("Add Transaction")
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime(2025, 8, 20))  # Default to today
            ticker_options = sorted(tracker.current_prices.keys())
            ticker = st.selectbox("Ticker", ["Cash"] + ticker_options, index=0 if ticker_options else 0)
        with col2:
            trans_type = st.selectbox("Type", ["Buy", "Sell", "Deposit", "Withdraw"])
            quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
            price = st.number_input("Price", min_value=0.0, step=0.01, value=tracker.current_prices.get(ticker, {'price': 0.0})['price'] if ticker != "Cash" and ticker in tracker.current_prices else 0.0)
            fee = st.number_input("Fee", min_value=0.0, value=0.0, step=0.01)
        submit = st.form_submit_button("Add Transaction")
        if submit:
            try:
                ticker_to_use = ticker if trans_type in ["Buy", "Sell"] else None
                tracker.add_transaction(date, ticker_to_use, trans_type, quantity, price, fee)
                st.session_state.data_changed = True
                st.success("Transaction added successfully!")
                st.rerun()
            except ValueError as e:
                st.error(f"Error: {e}")
