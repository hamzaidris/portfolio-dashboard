import streamlit as st
import time
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_add_transaction(tracker):
    st.header("Add Transaction")
    st.write("Add a new transaction to your portfolio.")

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", value=datetime.now(), key="add_trans_date")
    with col2:
        trans_type = st.selectbox("Transaction Type", ["Buy", "Sell", "Deposit", "Withdraw"], key="add_trans_type")

    cash = getattr(tracker, 'cash', 0.0)  # Fallback to 0.0 if attribute missing

    if trans_type in ["Buy", "Sell"]:
        ticker = st.selectbox("Stock Ticker", list(tracker.current_prices.keys()), key="add_trans_ticker")
        current_price = tracker.current_prices.get(ticker, {}).get('price', 0.0)
        price = st.number_input("Price (PKR)", value=current_price, step=0.01, key="add_trans_price")
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0, key="add_trans_quantity")
        fee = st.number_input("Fee (PKR)", min_value=0.0, value=0.0, step=0.01, key="add_trans_fee")
        total_cost = price * quantity + fee

        if st.button("Add Transaction", key="add_trans_submit"):
            if cash <= 0.0 and trans_type == "Buy":
                st.error("No cash available for this transaction.", icon="⚠️")
                time.sleep(5)
                st.rerun()
            elif price <= 0.0:
                st.error("Price must be greater than 0.", icon="⚠️")
                time.sleep(5)
                st.rerun()
            elif quantity <= 0.0:
                st.error("Quantity must be greater than 0.", icon="⚠️")
                time.sleep(5)
                st.rerun()
            elif trans_type == "Buy" and cash < total_cost:
                st.error(f"Insufficient cash available. Required: PKR {total_cost:.2f}, Available: PKR {cash:.2f}", icon="⚠️")
                time.sleep(5)
                st.rerun()
            else:
                try:
                    tracker.add_transaction(date, ticker, trans_type, quantity, price, fee)
                    st.success("Transaction has been added", icon="✅")
                    st.session_state.data_changed = True
                    time.sleep(5)
                    st.rerun()
                except ValueError as e:
                    st.error(str(e), icon="⚠️")
                    time.sleep(5)
                    st.rerun()
    else:
        amount = st.number_input("Amount (PKR)", min_value=0.0, step=1.0, key="add_trans_amount")
        fee = 0.0

        if st.button("Add Transaction", key="add_trans_submit"):
            if cash <= 0.0 and trans_type == "Withdraw":
                st.error("No cash available for withdrawal.", icon="⚠️")
                time.sleep(5)
                st.rerun()
            elif amount <= 0.0:
                st.error("Amount must be greater than 0.", icon="⚠️")
                time.sleep(5)
                st.rerun()
            else:
                try:
                    tracker.add_transaction(date, None, trans_type, amount, 0.0, fee)
                    st.success("Cash has been added" if trans_type == "Deposit" else "Cash has been withdrawn", icon="✅")
                    st.session_state.data_changed = True
                    time.sleep(5)
                    st.rerun()
                except ValueError as e:
                    st.error(str(e), icon="⚠️")
                    time.sleep(5)
                    st.rerun()

def render_sample_distribution(tracker):
    st.subheader("Sample Distribution")
    with st.form("distribute_cash_form"):
        date = st.date_input("Date", value=datetime(2025, 8, 21, 11, 38))
        cash = st.number_input("Cash to Add and Distribute (PKR)", min_value=0.0, step=100.0)
        sharia_only = st.checkbox("Distribute only to Sharia-compliant stocks", value=False)
        submit_calc = st.form_submit_button("Calculate Sample Distribution")
    if submit_calc:
        if cash <= 0.0:
            st.error("Cash amount must be greater than 0.", icon="⚠️")
            time.sleep(5)
            st.rerun()
        else:
            if sharia_only:
                sharia_allocations = {
                    ticker: alloc for ticker, alloc in tracker.target_allocations.items()
                    if tracker.current_prices.get(ticker, {'sharia': False})['sharia'] and alloc > 0
                }
                if not sharia_allocations:
                    st.error("No Sharia-compliant stocks with positive allocations.", icon="⚠️")
                    time.sleep(5)
                    st.rerun()
                else:
                    total_alloc = sum(sharia_allocations.values())
                    if total_alloc == 0:
                        st.error("Total allocation for Sharia-compliant stocks is 0.", icon="⚠️")
                        time.sleep(5)
                        st.rerun()
                    else:
                        normalized_allocations = {ticker: alloc / total_alloc * 100 for ticker, alloc in sharia_allocations.items()}
                        temp_tracker = PortfolioTracker()
                        temp_tracker.target_allocations = normalized_allocations
                        temp_tracker.current_prices = tracker.current_prices
                        dist_df = temp_tracker.calculate_distribution(cash)
                        st.session_state.dist_df = dist_df
                        st.write("Sample Distribution Results:")
                        st.dataframe(dist_df)
            else:
                total_alloc = sum(tracker.target_allocations.values())
                if total_alloc == 0:
                    st.error("Total allocation for stocks is 0.", icon="⚠️")
                    time.sleep(5)
                    st.rerun()
                else:
                    normalized_allocations = {ticker: alloc / total_alloc * 100 for ticker, alloc in tracker.target_allocations.items() if alloc > 0}
                    temp_tracker = PortfolioTracker()
                    temp_tracker.target_allocations = normalized_allocations
                    temp_tracker.current_prices = tracker.current_prices
                    dist_df = temp_tracker.calculate_distribution(cash)
                    st.session_state.dist_df = dist_df
                    st.write("Sample Distribution Results:")
                    st.dataframe(dist_df)
