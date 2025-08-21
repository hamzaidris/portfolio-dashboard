# trackerbazaar/cash.py

import streamlit as st
from trackerbazaar.tracker import PortfolioTracker   # ✅ correct import


def cash_ui():
    """Streamlit UI for managing cash in a portfolio."""
    st.header("💵 Manage Cash")

    tracker = PortfolioTracker()

    with st.form("cash_form"):
        portfolio_id = st.text_input("Portfolio ID")
        amount = st.number_input("Cash Amount", min_value=0.0, step=0.01)
        transaction_type = st.selectbox("Transaction Type", ["Deposit", "Withdrawal"])

        submitted = st.form_submit_button("Add Cash Transaction")

        if submitted:
            try:
                if transaction_type == "Deposit":
                    tracker.add_cash(portfolio_id, amount)
                else:
                    tracker.withdraw_cash(portfolio_id, amount)
                st.success(f"✅ {transaction_type} successful!")
            except Exception as e:
                st.error(f"❌ Failed to process transaction: {e}")
