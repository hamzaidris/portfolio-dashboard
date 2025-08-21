# trackerbazaar/add_dividend.py

import streamlit as st
from trackerbazaar.portfolios import PortfolioManager


def add_dividend_ui():
    """Streamlit UI for adding dividends to a portfolio."""
    st.header("💰 Add Dividend")

    portfolio_manager = PortfolioManager()

    with st.form("add_dividend_form"):
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
        amount = st.number_input("Dividend Amount", min_value=0.0, step=0.01)

        submitted = st.form_submit_button("Add Dividend")

        if submitted:
            try:
                portfolio_manager.add_dividend(
                    portfolio_id, str(date), ticker, amount
                )
                st.success("✅ Dividend added successfully!")
            except Exception as e:
                st.error(f"❌ Failed to add dividend: {e}")
