import streamlit as st
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_add_transaction(tracker):
    st.header("Add Transaction")
    st.write("Add a new transaction to your portfolio, including sample distribution for buying.")

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", value=datetime.now(), key="add_trans_date", help="Select transaction date")
    with col2:
        trans_type = st.selectbox("Transaction Type", ["Buy", "Sell", "Deposit", "Withdraw"], key="add_trans_type", help="Choose transaction type")

    if trans_type in ["Buy", "Sell"]:
        ticker = st.selectbox("Stock Ticker", list(tracker.current_prices.keys()), key="add_trans_ticker", help="Select a stock ticker")
        current_price = tracker.current_prices.get(ticker, {}).get('price', 0.0)
        price = st.number_input("Price (PKR)", value=current_price, step=0.01, key="add_trans_price", help="Enter or edit price")
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0, key="add_trans_quantity", help="Enter number of shares or amount")
        fee = st.number_input("Fee (PKR)", min_value=0.0, value=0.0, step=0.01, key="add_trans_fee", help="Enter transaction fee")
    else:
        ticker = None
        price = 0.0
        quantity = st.number_input("Amount (PKR)", min_value=0.0, step=1.0, key="add_trans_amount", help="Enter amount to deposit or withdraw")
        fee = 0.0

    # Add Sample Distribution section for Buy transactions
    if trans_type == "Buy" and tracker.target_allocations:
        st.subheader("Sample Distribution")
        cash_to_distribute = st.number_input("Cash to Distribute (PKR)", min_value=0.0, step=1.0, key="distribute_cash", help="Enter amount to distribute across stocks")
        if cash_to_distribute > 0:
            distribution_df = tracker.calculate_distribution(cash_to_distribute)
            if not distribution_df.empty:
                st.dataframe(
                    distribution_df,
                    column_config={
                        "Quantity": st.column_config.NumberColumn("Shares"),
                        "Price": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Fee": st.column_config.NumberColumn(format="PKR %.2f"),
                        "SST": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Net Invested": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Leftover": st.column_config.NumberColumn(format="PKR %.2f")
                    },
                    use_container_width=True
                )
                if st.button("Use Distribution for This Transaction", key="use_distribution", help="Apply the calculated distribution to this transaction"):
                    selected_stock = st.selectbox("Select Stock from Distribution", distribution_df["Stock"].tolist(), key="select_dist_stock")
                    selected_row = distribution_df[distribution_df["Stock"] == selected_stock].iloc[0]
                    quantity = selected_row["Quantity"]
                    price = selected_row["Price"]
                    fee = selected_row["Fee"]
                    st.success(f"Applied distribution: {quantity} shares of {selected_stock} at PKR {price} with fee PKR {fee}")
            else:
                st.warning("No distribution calculated. Ensure target allocations are set.")

    if st.button("Add Transaction", key="add_trans_submit", help="Submit the transaction"):
        try:
            tracker.add_transaction(date, ticker, trans_type, quantity, price, fee)
            if trans_type == "Deposit":
                st.success("Cash has been added")
            else:
                st.success("Transaction has been added")
            st.session_state.data_changed = True
            st.rerun()
        except ValueError as e:
            st.error(str(e))
