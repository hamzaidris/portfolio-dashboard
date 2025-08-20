import streamlit as st
import pandas as pd
from datetime import datetime
from .tracker import PortfolioTracker

def render_cash(tracker):
    st.header("Cash Summary")
    tabs = st.tabs(["Cash Flow", "Add Cash", "Cash Available", "Withdraw Cash"])

    with tabs[0]:
        cash_df = tracker.get_cash_summary()
        if not cash_df.empty:
            cash_df['date'] = pd.to_datetime(cash_df['date']).dt.strftime('%Y-%m-%d')
            st.dataframe(
                cash_df,
                column_config={
                    "quantity": st.column_config.NumberColumn(format="PKR %.2f")
                },
                use_container_width=True
            )
        else:
            st.info("No cash transactions recorded. Add a deposit to start.")
        st.metric("Current Cash Balance", f"PKR {tracker.cash:,.2f}")
        dashboard = tracker.get_dashboard()
        st.metric("Total Invested Amount", f"PKR {dashboard['Total Invested']:,.2f}")

    with tabs[1]:
        with st.form("add_cash_form"):
            date = st.date_input("Deposit Date", value=datetime.now())
            amount = st.number_input("Deposit Amount (PKR)", min_value=0.0, step=100.0)
            submit = st.form_submit_button("Add Cash")
            if submit:
                try:
                    tracker.add_transaction(date, None, 'Deposit', amount, 0.0)
                    st.success("Cash deposited successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

    with tabs[2]:
        cash_to_invest = tracker.get_cash_to_invest()
        st.metric("Cash Available", f"PKR {cash_to_invest:,.2f}")
        deposits_df = pd.DataFrame(tracker.cash_deposits)
        if not deposits_df.empty:
            deposits_df['date'] = pd.to_datetime(deposits_df['date']).dt.strftime('%Y-%m-%d')
            st.dataframe(
                deposits_df,
                column_config={
                    "amount": st.column_config.NumberColumn(format="PKR %.2f")
                },
                use_container_width=True
            )
        else:
            st.info("No new cash deposits recorded.")
        st.write(f"Previous Cash Available: PKR {tracker.cash:,.2f}")

    with tabs[3]:
        st.subheader("Withdraw Cash")
        with st.form("withdraw_cash_form"):
            date = st.date_input("Withdrawal Date", value=datetime.now())
            amount = st.number_input("Withdrawal Amount (PKR)", min_value=0.0, step=100.0)
            submit = st.form_submit_button("Withdraw Cash")
            if submit:
                try:
                    tracker.add_transaction(date, None, 'Withdraw', amount, 0.0)
                    st.success("Cash withdrawn successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")
