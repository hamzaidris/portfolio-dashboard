import streamlit as st
import pandas as pd
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_cash(tracker):
    st.header("Cash Management")
    st.write("Manage your cash deposits, withdrawals, and view total cash.")

    tabs = st.tabs(["Cash Flow", "Add Cash", "Cash Available", "Withdrawals"])

    with tabs[0]:
        cash_df = tracker.get_cash_summary()
        if not cash_df.empty:
            cash_df['date'] = pd.to_datetime(cash_df['date']).dt.strftime('%Y-%m-%d')
            st.dataframe(
                cash_df,
                column_config={"quantity": st.column_config.NumberColumn("Amount", format="PKR %.2f")},
                use_container_width=True
            )
            total_cash = sum(trans['total'] for trans in tracker.transactions if trans['type'] == 'Deposit')
            st.write(f"**Total Cash Deposited:** PKR {total_cash:,.2f}")
        else:
            st.info("No cash transactions recorded.")

    with tabs[1]:
        st.subheader("Add Cash")
        date = st.date_input("Date", value=datetime.now())
        amount = st.number_input("Amount (PKR)", min_value=0.0, step=1.0)
        if st.button("Add Cash", help="Add cash to your portfolio"):
            try:
                tracker.add_transaction(date, None, "Deposit", amount, 0.0)
                st.success("Cash has been added")
                st.session_state.data_changed = True
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    with tabs[2]:
        st.subheader("Cash Available")
        st.write(f"**Available Cash:** PKR {tracker.cash:,.2f}")

    with tabs[3]:
        st.subheader("Withdrawals")
        date = st.date_input("Date", value=datetime.now())
        amount = st.number_input("Amount (PKR)", min_value=0.0, step=1.0)
        if st.button("Withdraw", help="Withdraw cash from your portfolio"):
            try:
                tracker.add_transaction(date, None, "Withdraw", amount, 0.0)
                st.success("Transaction has been added")
                st.session_state.data_changed = True
                st.rerun()
            except ValueError as e:
                st.error(str(e))
