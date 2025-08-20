import streamlit as st
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_add_transaction(tracker):
    st.header("Add Transaction")
    st.write("Add a new transaction to your portfolio.")

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", value=datetime.now())
    with col2:
        trans_type = st.selectbox("Transaction Type", ["Buy", "Sell", "Deposit", "Withdraw"])

    if trans_type in ["Buy", "Sell"]:
        ticker = st.selectbox("Stock Ticker", list(tracker.current_prices.keys()))
        # Automatically set current price, with editable override
        current_price = tracker.current_prices.get(ticker, {}).get('price', 0.0)
        price = st.number_input("Price (PKR)", value=current_price, step=0.01)
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
        fee = st.number_input("Fee (PKR)", min_value=0.0, value=0.0, step=0.01)
    else:
        ticker = None
        price = 0.0
        quantity = st.number_input("Amount (PKR)", min_value=0.0, step=1.0)
        fee = 0.0

    if st.button("Add Transaction"):
        try:
            tracker.add_transaction(date, ticker, trans_type, quantity, price, fee)
            if trans_type == "Deposit":
                st.success("Cash has been added")
            else:
                st.success("Transaction has been added")
            st.session_state.data_changed = True
            st.rerun()
        except ValueError as e:
            st.error(str(e))
