import streamlit as st
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.portfolio_tracker import PortfolioTracker  # ✅ fixed import


def show_portfolio_ui(current_user):
    st.subheader("📊 Portfolio Overview")

    if not current_user:
        st.warning("Please log in to view your portfolios.")
        return

    pm = PortfolioManager()
    portfolios = pm.list_portfolios(current_user)

    if not portfolios:
        st.info("No portfolios available. Please create one first.")
        return

    selected_portfolio = st.selectbox("Select Portfolio", portfolios)

    tracker = pm.load_portfolio(selected_portfolio, current_user)

    if not tracker:
        st.error("Failed to load portfolio.")
        return

    st.markdown(f"### Portfolio: **{selected_portfolio}**")

    # Portfolio Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"{tracker.total_invested():,.2f}")
    with col2:
        st.metric("Current Value", f"{tracker.current_value():,.2f}")
    with col3:
        st.metric("Unrealized P/L", f"{tracker.unrealized_pl():,.2f}")

    st.divider()

    # Holdings Table
    holdings = tracker.get_holdings()
    if holdings.empty:
        st.info("No transactions found in this portfolio.")
    else:
        st.dataframe(holdings, use_container_width=True)

    # Transactions History
    st.markdown("#### 📜 Transaction History")
    txns = tracker.get_transactions()
    if txns.empty:
        st.info("No transactions recorded.")
    else:
        st.dataframe(txns, use_container_width=True)
