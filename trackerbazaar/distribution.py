import streamlit as st
import pandas as pd
import plotly.express as px
from trackerbazaar.tracker import PortfolioTracker

def render_distribution(tracker):
    st.header("Distribution Analysis")

    # Display current target allocations with graph and table
    dist_list = [
        {'Stock': ticker, 'Target Allocation %': alloc}
        for ticker, alloc in tracker.target_allocations.items() if alloc > 0
    ]
    dist_df = pd.DataFrame(dist_list)
    st.subheader("Current Target Allocations")
    if not dist_df.empty:
        fig_dist = px.bar(
            dist_df,
            x='Stock',
            y='Target Allocation %',
            title='Target Allocation',
            color_discrete_map={'Target Allocation %': '#00CC96'}
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        alloc_df = {ticker: [alloc] for ticker, alloc in tracker.target_allocations.items() if alloc > 0}
        st.table({k: [f"{v:.2f}%" for v in vs] for k, vs in alloc_df.items()})
    else:
        st.info("No target allocations set. Add allocations below.")

    # Edit Target Allocations form
    st.subheader("Edit Target Allocations")
    with st.form("edit_allocations_form"):
        st.write("Select stocks and enter target allocation percentages (must sum to 100%)")
        selected_tickers = st.multiselect(
            "Select Stocks",
            options=sorted(tracker.current_prices.keys()),
            default=[ticker for ticker, alloc in tracker.target_allocations.items() if alloc > 0]
        )
        new_allocations = {}
        if selected_tickers:
            cols = st.columns(min(len(selected_tickers), 5))
            for i, ticker in enumerate(selected_tickers):
                with cols[i % 5]:
                    new_allocations[ticker] = st.number_input(
                        f"{ticker} (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=tracker.target_allocations.get(ticker, 0.0),
                        step=0.1,
                        key=f"alloc_{ticker}"
                    )
        submit = st.form_submit_button("Update Allocations")
        if submit:
            try:
                tracker.update_target_allocations(new_allocations)
                st.success("Target allocations updated successfully!")
                st.rerun()
            except ValueError as e:
                st.error(f"Error: {e}")