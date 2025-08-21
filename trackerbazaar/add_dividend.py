import streamlit as st
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker
from trackerbazaar.portfolios import PortfolioManager

def render_add_dividend(tracker):
    portfolio_manager = PortfolioManager()
    email = st.session_state.get('logged_in_user')
    portfolio_name = st.session_state.get('selected_portfolio')

    st.header("Add Dividend")
    with st.form("dividend_form"):
        ticker_options = sorted(tracker.current_prices.keys())
        ticker = st.selectbox("Ticker", ticker_options, index=0 if ticker_options else None)
        amount = st.number_input("Dividend Amount (PKR)", min_value=0.0, step=0.01)
        submit = st.form_submit_button("Add Dividend")

        if submit:
            if amount <= 0:
                st.error("Dividend amount must be greater than 0.")
            else:
                try:
                    tracker.add_dividend(ticker, amount)
                    portfolio_manager.save_portfolio(portfolio_name, email, tracker)
                    st.session_state.data_changed = True
                    st.success("Dividend added successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")
