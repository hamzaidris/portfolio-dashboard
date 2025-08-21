# trackerbazaar/add_transaction.py

import streamlit as st
from trackerbazaar.portfolios import PortfolioManager


def add_transaction_ui():
    """Streamlit UI for adding a transaction."""
    st.header("➕ Add Transaction")

    portfolio_manager = PortfolioManager()

    with st.form("add_transaction_form"):
        email = st.session_state.get("logged_in_user")
        if not email:
            st.error("⚠️ Please log in first.")
            return

        portfolio_list = portfolio_manager.list_portfolios(email)
        if not portfolio_list:
            st.warning("You don’t have any portfolios yet. Create one first.")
            return

        portfolio_id = st.selectbox("Select Portfolio", [p[0] for p in portfolio_list])
        date = st.date_input("Date")
        ticker = st.text_input("Ticker Symbol")
        transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell"])
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price per Share", min_value=0.0, step=0.01)
        brokerage = st.number_input("Brokerage Fee", min_value=0.0, step=0.01)

        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            try:
                portfolio_manager.add_transaction(
                    portfolio_id, str(date), ticker, transaction_type, quantity, price, brokerage
                )
                st.success("✅ Transaction added successfully!")
            except Exception as e:
                st.error(f"❌ Failed to add transaction: {e}")
