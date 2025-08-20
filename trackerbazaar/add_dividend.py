import streamlit as st
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_add_dividend(tracker):
    st.header("Add Dividend")
    with st.form("dividend_form"):
        ticker_options = sorted(tracker.current_prices.keys())
        ticker = st.selectbox("Ticker", ticker_options, index=0 if ticker_options else None)
        amount = st.number_input("Dividend Amount (PKR)", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Dividend")
        if submit:
            try:
                tracker.add_dividend(ticker, amount)
                st.session_state.data_changed = True
                st.success("Dividend added successfully!")
                st.rerun()
            except ValueError as e:
                st.error(f"Error: {e}")
