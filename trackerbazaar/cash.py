import streamlit as st
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ fixed import


def show_cash_ui(current_user):
    st.title("💰 Portfolio Cash Manager")

    if not current_user:
        st.warning("Please log in to manage cash.")
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

    # ---- Current Balance ----
    balance = tracker.get_cash_balance()
    st.metric("Current Cash Balance", f"PKR {balance:,.2f}")

    # ---- Deposit / Withdraw ----
    st.markdown("### Manage Cash")
    col1, col2 = st.columns(2)

    with col1:
        deposit_amount = st.number_input("Deposit Amount", min_value=0.0, step=100.0)
        if st.button("➕ Deposit"):
            try:
                tracker.deposit_cash(deposit_amount)
                pm.save_portfolio(selected_portfolio, current_user, tracker)
                st.success(f"Deposited PKR {deposit_amount:,.2f}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to deposit: {e}")

    with col2:
        withdraw_amount = st.number_input("Withdraw Amount", min_value=0.0, step=100.0)
        if st.button("➖ Withdraw"):
            try:
                tracker.withdraw_cash(withdraw_amount)
                pm.save_portfolio(selected_portfolio, current_user, tracker)
                st.success(f"Withdrew PKR {withdraw_amount:,.2f}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to withdraw: {e}")
