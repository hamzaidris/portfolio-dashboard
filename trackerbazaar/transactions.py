# transactions.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_transactions(selected_portfolio: str, user_email: str):
    """Display and manage transactions for the selected portfolio."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"💹 Transactions — {selected_portfolio}")

    # ---- Add New Transaction ----
    with st.expander("➕ Add New Transaction", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.text_input("Ticker Symbol (e.g., LUCK, MUGHAL)")
            date = st.date_input("Transaction Date")
            tx_type = st.selectbox("Type", ["Buy", "Sell"])
        with col2:
            quantity = st.number_input("Quantity", min_value=1, step=1)
            price = st.number_input("Price per Share (PKR)", min_value=0.0, step=0.1)
            fees = st.number_input("Brokerage Fee (PKR)", min_value=0.0, step=0.1)

        if st.button("Add Transaction", use_container_width=True, type="primary"):
            if not ticker:
                st.warning("Please enter a ticker symbol.")
            else:
                try:
                    tracker.add_transaction(
                        ticker=ticker.strip().upper(),
                        date=str(date),
                        tx_type=tx_type,
                        quantity=quantity,
                        price=price,
                        fees=fees,
                    )
                    portfolio_manager.save_portfolio(selected_portfolio, user_email, tracker)
                    st.success(f"Transaction added for {ticker} ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add transaction: {e}")

    st.divider()

    # ---- Transactions Table ----
    if not tracker.transactions:
        st.info("No transactions yet. Add your first trade above.")
        return

    df = pd.DataFrame(tracker.transactions)
    st.dataframe(df, use_container_width=True)

    # ---- Download Option ----
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Transactions as CSV",
        data=csv,
        file_name=f"{selected_portfolio}_transactions.csv",
        mime="text/csv",
    )
