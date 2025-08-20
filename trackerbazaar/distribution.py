import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_distribution(tracker):
    st.header("Distribution Analysis")
    dist_list = [
        {'Stock': ticker, 'Target Allocation %': alloc}
        for ticker, alloc in tracker.target_allocations.items() if alloc > 0
    ]
    dist_df = pd.DataFrame(dist_list)
    if not dist_df.empty:
        dist_df['Select'] = False
        edited_df = st.data_editor(
            dist_df,
            column_config={
                "Target Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                "Select": st.column_config.CheckboxColumn()
            },
            use_container_width=True,
            hide_index=True
        )
        selected = edited_df[edited_df['Select']].index.tolist()
        if selected:
            selected_ticker = edited_df.loc[selected[0], 'Stock']
            st.subheader(f"Edit or Remove {selected_ticker}")
            new_percentage = st.number_input(
                f"New Percentage for {selected_ticker} (%)",
                min_value=0.0,
                max_value=100.0,
                value=tracker.target_allocations.get(selected_ticker, 0.0),
                step=0.1,
                key=f"edit_alloc_{selected_ticker}"
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Percentage"):
                    new_allocations = {ticker: tracker.target_allocations.get(ticker, 0.0) for ticker in tracker.current_prices.keys()}
                    new_allocations[selected_ticker] = new_percentage
                    try:
                        tracker.update_target_allocations(new_allocations)
                        st.success(f"Percentage for {selected_ticker} updated to {new_percentage}%")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.button("Remove Stock"):
                    new_allocations = {ticker: tracker.target_allocations.get(ticker, 0.0) for ticker in tracker.current_prices.keys()}
                    new_allocations[selected_ticker] = 0.0
                    try:
                        tracker.update_target_allocations(new_allocations)
                        st.success(f"{selected_ticker} removed from distribution.")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Error: {e}")
            if len(selected) > 1:
                st.warning("Please select only one stock to edit or remove.")
        fig_dist = px.bar(
            dist_df,
            x='Stock',
            y='Target Allocation %',
            title='Target Allocation',
            color_discrete_map={'Target Allocation %': '#00CC96'}
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No target allocations set. Add allocations below.")

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
