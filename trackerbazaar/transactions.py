# transactions.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_transactions(selected_portfolio: str, user_email: str):
    """Trade Manager for recording and viewing portfolio transactions."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"💹 Trade Manager — {selected_portfolio}")

    # ---- Add Transaction Form ----
    with st.form("add_transaction_form", clear_on_submit=True):
        st.markdown("### ➕ Add Transaction")

        col1, col2, col3 = st.columns(3)
        with col1:
            stock = st.text_input("Stock Symbol")
        with col2:
            tx_type = st.selectbox("Transaction Type", ["Buy", "Sell"])
        with col3:
            quantity = st.number_input("Quantity", min_value=1, step=1)

        col4, col5, col6 = st.columns(3)
        with col4:
            price = st.number_input("Price per Share (PKR)", min_value=0.0, step=0.01)
        with col5:
            fee = st.number_input("Brokerage Fee (PKR)", min_value=0.0, step=0.01)
        with col6:
            date = st.date_input("Date")

        submitted = st.form_submit_button("💾 Save Transaction")

        if submitted:
            try:
                tracker.add_transaction({
                    "stock": stock.upper(),
                    "type": tx_type,
                    "quantity": quantity,
                    "price": price,
                    "fee": fee,
                    "date": str(date)
                })
                portfolio_manager.save_portfolio(selected_portfolio, user_email, tracker)
                st.success(f"Transaction added: {tx_type} {quantity} {stock} @ {price}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add transaction: {e}")

    st.divider()

    # ---- Transaction History ----
    st.subheader("📑 Transaction History")
    if tracker.transactions:
        tx_df = pd.DataFrame(tracker.transactions)

        # Clean column names
        tx_df = tx_df.rename(columns={
            "stock": "Stock",
            "type": "Type",
            "quantity": "Qty",
            "price": "Price",
            "fee": "Fee",
            "date": "Date"
        })

        st.dataframe(tx_df, use_container_width=True)

        # ---- Chart of Buys vs Sells ----
        st.subheader("📊 Buy vs Sell Volume")
        chart_df = tx_df.groupby("Type")["Qty"].sum().reset_index()
        st.bar_chart(chart_df.set_index("Type"))

    else:
        st.info("No transactions yet. Add one above ⬆️")
