import streamlit as st
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ fixed import
from trackerbazaar.data import DB_FILE


def add_dividend_ui(current_user):
    st.subheader("💰 Add Dividend")

    if not current_user:
        st.warning("Please log in to add dividends.")
        return

    pm = PortfolioManager()
    portfolios = pm.list_portfolios(current_user)

    if not portfolios:
        st.info("No portfolios found. Please create one first.")
        return

    selected_portfolio = st.selectbox("Select Portfolio", portfolios)
    dividend_date = st.date_input("Dividend Date")
    stock_symbol = st.text_input("Stock Symbol")
    dividend_amount = st.number_input("Dividend Amount", min_value=0.0, step=0.01)

    if st.button("Add Dividend"):
        tracker = pm.load_portfolio(selected_portfolio, current_user)
        if tracker:
            tracker.add_dividend(stock_symbol, dividend_amount, str(dividend_date))
            pm.save_portfolio(selected_portfolio, current_user, tracker)
            st.success(f"Dividend added for {stock_symbol} on {dividend_date}")
            st.rerun()  # ✅ modern rerun API
        else:
            st.error("Failed to load portfolio.")
