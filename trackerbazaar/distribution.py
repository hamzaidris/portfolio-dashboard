# trackerbazaar/distribution.py
import streamlit as st
from trackerbazaar.tracker import PortfolioTracker

def render_distribution(tracker):
    st.header("Distribution")
    st.write("Set the target percentage allocation for each stock in your portfolio.")

    # Get available tickers from current prices
    tickers = list(tracker.current_prices.keys())
    current_allocations = tracker.target_allocations.copy()

    # Input fields for each ticker
    allocations = {}
    total_alloc = 0.0
    for ticker in tickers:
        alloc = st.number_input(
            f"Allocation for {ticker} (%)",
            min_value=0.0,
            max_value=100.0,
            value=current_allocations.get(ticker, 0.0),
            step=0.1,
            key=f"dist_alloc_{ticker}"
        )
        allocations[ticker] = alloc
        total_alloc += alloc

    st.write(f"**Total Allocation: {total_alloc:.2f}%**")
    if st.button("Save Allocations", key="save_dist_allocations"):
        if 99.9 <= total_alloc <= 100.1:  # Allow slight float precision
            tracker.update_target_allocations(allocations)
            st.success("Target allocations saved successfully!")
            st.session_state.data_changed = True
            st.rerun()
        else:
            st.error("Total allocation must sum to 100%. Current total is {total_alloc:.2f}%.")

    # Display current allocations
    if current_allocations:
        st.subheader("Current Target Allocations")
        alloc_df = {ticker: [alloc] for ticker, alloc in current_allocations.items() if alloc > 0}
        if alloc_df:
            st.table({k: [f"{v:.2f}%" for v in vs] for k, vs in alloc_df.items()})
        else:
            st.info("No target allocations set yet.")
