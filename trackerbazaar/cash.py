import streamlit as st
import time
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_cash(tracker):
    st.header("Cash Management")
    st.write("Manage your cash balance and add new cash transactions.")

    # Display current cash balance with fallback
    cash = getattr(tracker, 'cash', 0.0)  # Fallback to 0.0 if attribute missing
    st.subheader("Current Cash Balance")
    st.write(f"PKR {cash:.2f}")

    # Add Cash Form
    st.subheader("Add Cash")
    with st.form(key="add_cash_form"):
        date = st.date_input("Date", value=datetime.now(), key="cash_date")
        amount = st.number_input("Amount (PKR)", min_value=0.0, step=1.0, key="cash_amount")
        if st.form_submit_button("Add Cash"):
            try:
                tracker.add_transaction(date, None, "Deposit", amount, 0.0, 0.0)
                st.success("Cash has been added successfully!", icon="✅")
                st.session_state.data_changed = True
                time.sleep(5)
                st.rerun()
            except ValueError as e:
                st.error(str(e), icon="⚠️")
                time.sleep(5)
                st.rerun()

    # Withdraw Cash Form
    st.subheader("Withdraw Cash")
    with st.form(key="withdraw_cash_form"):
        date = st.date_input("Date", value=datetime.now(), key="withdraw_date")
        amount = st.number_input("Amount (PKR)", min_value=0.0, step=1.0, key="withdraw_amount")
        if st.form_submit_button("Withdraw Cash"):
            try:
                if amount > cash:
                    raise ValueError("Insufficient cash balance for withdrawal")
                tracker.add_transaction(date, None, "Withdraw", amount, 0.0, 0.0)
                st.success("Cash has been withdrawn successfully!", icon="✅")
                st.session_state.data_changed = True
                time.sleep(5)
                st.rerun()
            except ValueError as e:
                st.error(str(e), icon="⚠️")
                time.sleep(5)
                st.rerun()
