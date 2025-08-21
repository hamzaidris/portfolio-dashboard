import streamlit as st

def render_guide():
    st.header("Guide to Investment Tracking")
    st.write("Step-by-step guide to get started with TrackerBazaar:")

    st.subheader("1. Load Data")
    st.write("Ensure market-data.json and kmi_shares.txt are in the repository. These files provide stock prices and Sharia compliance.")

    st.subheader("2. Add Cash")
    st.write("Go to the 'Cash' page, use 'Add Cash' to deposit funds into your portfolio. This increases your cash balance for investments.")

    st.subheader("3. Set Target Allocations")
    st.write("Go to the 'Distribution' page, select stocks in 'Edit Target Allocations', and set percentages (must sum to 100%). Update to save.")

    st.subheader("4. Calculate Sample Distribution")
    st.write("In 'Distribution', input cash in 'Sample Distribution' to see how it would be allocated based on targets (with fees). This is a preview; it doesn't execute buys.")

    st.subheader("5. Add Transactions")
    st.write("Go to 'Add Transaction' to buy/sell stocks, deposit/withdraw cash. Transactions update your portfolio automatically.")

    st.subheader("6. Monitor Portfolio")
    st.write("View 'Dashboard' for overall metrics, 'Portfolio' for holdings details, 'Stock Explorer' for market data, and 'Notifications' for alerts.")

    st.subheader("7. Rebalance and Edit")
    st.write("Use 'Distribution' to edit/remove allocations, 'Broker Fees' to customize fees, and 'Current Prices' to update stock prices.")

    st.subheader("8. Withdraw Cash")
    st.write("In 'Cash', use 'Withdraw Cash' to remove funds from your portfolio.")

    st.write("Repeat steps 3-5 for rebalancing as needed. Track your journey with charts on the Dashboard.")
