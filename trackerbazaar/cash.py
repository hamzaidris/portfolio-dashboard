# cash.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_cash(selected_portfolio: str, user_email: str):
    """Display and manage cash balance for the selected portfolio."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"💵 Cash Management — {selected_portfolio}")

    # ---- Current Balance ----
    st.metric("Current Cash Balance", f"PKR {tracker.cash_balance:,.2f}")

    # ---- Add Cash ----
    with st.expander("➕ Add Cash", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            amount = st.number_input("Amount to Add (PKR)", min_value=0.0, step=100.0)
        with col2:
            if st.button("Add", use_container_width=True, type="primary", key="add_cash"):
                try:
                    tracker.add_cash(amount)
                    portfolio_manager.save_portfolio(selected_portfolio, user_email, tracker)
                    st.success(f"Added PKR {amount:,.2f} ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add cash: {e}")

    # ---- Withdraw Cash ----
    with st.expander("➖ Withdraw Cash", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            amount = st.number_input("Amount to Withdraw (PKR)", min_value=0.0, step=100.0)
        with col2:
            if st.button("Withdraw", use_container_width=True, type="secondary", key="withdraw_cash"):
                try:
                    tracker.withdraw_cash(amount)
                    portfolio_manager.save_portfolio(selected_portfolio, user_email, tracker)
                    st.success(f"Withdrew PKR {amount:,.2f} ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to withdraw cash: {e}")

    st.divider()

    # ---- Cash History ----
    if not tracker.cash_history:
        st.info("No cash transactions yet.")
    else:
        df = pd.DataFrame(tracker.cash_history)
        st.dataframe(df, use_container_width=True)

        # Download option
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Cash History as CSV",
            data=csv,
            file_name=f"{selected_portfolio}_cash_history.csv",
            mime="text/csv",
        )
