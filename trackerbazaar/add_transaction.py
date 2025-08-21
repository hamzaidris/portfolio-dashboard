import streamlit as st
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ fixed import


def show_add_transaction_ui(current_user):
    st.title("📝 Add Transaction")

    if not current_user:
        st.warning("Please log in to add transactions.")
        return

    pm = PortfolioManager()
    portfolios = pm.list_portfolios(current_user)

    if not portfolios:
        st.info("No portfolios found. Please create one first.")
        return

    selected_portfolio = st.selectbox("Select Portfolio", portfolios)

    tracker = pm.load_portfolio(selected_portfolio, current_user)
    if not tracker:
        st.error("Failed to load portfolio.")
        return

    # ---- Transaction Form ----
    st.markdown("### New Transaction")
    col1, col2 = st.columns(2)

    with col1:
        ticker = st.text_input("Stock Symbol (e.g., LUCK, HBL, OGDC)").upper()
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price per Share (PKR)", min_value=0.0, step=1.0)

    with col2:
        txn_type = st.radio("Transaction Type", ["Buy", "Sell"], horizontal=True)
        brokerage = st.number_input("Brokerage Fee (PKR)", min_value=0.0, step=10.0)

    if st.button("💾 Save Transaction"):
        try:
            if txn_type == "Buy":
                tracker.buy_stock(ticker, quantity, price, brokerage)
            else:
                tracker.sell_stock(ticker, quantity, price, brokerage)

            pm.save_portfolio(selected_portfolio, current_user, tracker)
            st.success(f"{txn_type} transaction saved for {ticker}")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save transaction: {e}")
