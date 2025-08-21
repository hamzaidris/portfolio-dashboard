import streamlit as st
import pandas as pd
from trackerbazaar.tracker import PortfolioTracker

def render_portfolio(tracker):
    st.header("Portfolio Summary")
    st.write("Overview of your current holdings and cash in hand.")
    
    # Safety: default to empty DF if None is returned
    portfolio_df = tracker.get_portfolio() or pd.DataFrame()
    if not portfolio_df.empty:
        st.dataframe(
            portfolio_df,
            column_config={
                "Market Value": st.column_config.NumberColumn(format="PKR %.2f"),
                "Total Invested": st.column_config.NumberColumn(format="PKR %.2f"),
                "Gain/Loss": st.column_config.NumberColumn(format="PKR %.2f"),
                "% Gain": st.column_config.NumberColumn(format="%.2f%"),
                "ROI %": st.column_config.NumberColumn(format="%.2f%"),
                "Current Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                "Target Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                "Allocation Delta %": st.column_config.NumberColumn(format="%.2f%"),
                "CGT (Potential)": st.column_config.NumberColumn(format="PKR %.2f")
            },
            use_container_width=True
        )
        st.write(f"**Cash in Hand:** PKR {tracker.cash:,.2f}")
    else:
        st.info("Your portfolio is empty. Add transactions to get started.")
