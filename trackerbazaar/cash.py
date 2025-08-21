# cash.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_cash(selected_portfolio: str, user_email: str):
    """Cash Manager — record deposits/withdrawals and show balance."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"💵 Cash Manager — {selected_portfolio}")

    # ---- Add Cash Transaction ----
    with st.form("cash_form", clear_on_submit=True):
        st.markdown("### ➕ Add Cash Transaction")

        col1, col2, col3 = st.columns(3)
        with col1:
            txn_type = st.selectbox("Type", ["Deposit", "Withdrawal"])
        with col2:
            amount = st.number_input("Amount (PKR)", min_value=0.0, step=0.01)
        with col3:
            date = st.date_input("Date")

        submitted = st.form_submit_button("💾 Save Transaction")

        if submitted:
            try:
                tracker.add_cash({
                    "type": txn_type,
                    "amount": amount,
                    "date": str(date)
                })
                portfolio_manager.save_portfolio(selected_portfolio, user_email, tracker)
                st.success(f"{txn_type} of {amount:,.2f} PKR recorded.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save cash transaction: {e}")

    st.divider()

    # ---- Cash History ----
    st.subheader("📑 Cash Transactions")
    if tracker.cash:
        cash_df = pd.DataFrame(tracker.cash)

        cash_df = cash_df.rename(columns={
            "type": "Type",
            "amount": "Amount",
            "date": "Date"
        })

        st.dataframe(cash_df, use_container_width=True)

        # ---- Calculate Balance ----
        deposits = cash_df[cash_df["Type"] == "Deposit"]["Amount"].sum()
        withdrawals = cash_df[cash_df["Type"] == "Withdrawal"]["Amount"].sum()
        balance = deposits - withdrawals

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Deposits", f"{deposits:,.2f} PKR")
        col2.metric("Total Withdrawals", f"{withdrawals:,.2f} PKR")
        col3.metric("Available Balance", f"{balance:,.2f} PKR")

        # ---- Trend chart ----
        st.subheader("📊 Cash Balance Trend")
        cash_df["Net"] = cash_df.apply(
            lambda row: row["Amount"] if row["Type"] == "Deposit" else -row["Amount"], axis=1
        )
        cash_df["Cumulative Balance"] = cash_df["Net"].cumsum()

        st.line_chart(cash_df.set_index("Date")["Cumulative Balance"])

    else:
        st.info("No cash transactions recorded yet. Add one above ⬆️")
