import streamlit as st
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ fixed import
from trackerbazaar.data import DB_FILE


def add_transaction_ui(current_user):
    st.subheader("➕ Add Transaction")

    if not current_user:
        st.warning("Please log in to add transactions.")
        return

    pm = PortfolioManager()
    portfolios = pm.list_portfolios(current_user)

    if not portfolios:
        st.info("No portfolios found. Please create one first.")
        return

    selected_portfolio = st.selectbox("Select Portfolio", portfolios)
    txn_date = st.date_input("Transaction Date")
    stock_symbol = st.text_input("Stock Symbol")
    txn_type = st.radio("Transaction Type", ["Buy", "Sell"], horizontal=True)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    price = st.number_input("Price per Share", min_value=0.0, step=0.01)
    brokerage = st.number_input("Brokerage Fee", min_value=0.0, step=0.01)

    if st.button("Save Transaction"):
        tracker = pm.load_portfolio(selected_portfolio, current_user)
        if tracker:
            tracker.add_transaction(
                symbol=stock_symbol,
                txn_type=txn_type,
                quantity=quantity,
                price=price,
                brokerage=brokerage,
                date=str(txn_date),
            )
            pm.save_portfolio(selected_portfolio, current_user, tracker)
            st.success(f"{txn_type} transaction saved for {stock_symbol}")
            st.rerun()  # ✅ modern rerun API
        else:
            st.error("Failed to load portfolio.")
