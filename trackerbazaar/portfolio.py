import streamlit as st
import pandas as pd
import plotly.express as px
from trackerbazaar.tracker import PortfolioTracker

def render_portfolio(tracker):
    st.header("Portfolio Summary")
    portfolio_df = tracker.get_portfolio()
    if not portfolio_df.empty:
        st.dataframe(
            portfolio_df,
            column_config={
                "Market Value": st.column_config.NumberColumn(format="PKR %.2f"),
                "Total Invested": st.column_config.NumberColumn(format="PKR %.2f"),
                "Gain/Loss": st.column_config.NumberColumn(format="PKR %.2f"),
                "Dividends": st.column_config.NumberColumn(format="PKR %.2f"),
                "% Gain": st.column_config.NumberColumn(format="%.2f%"),
                "ROI %": st.column_config.NumberColumn(format="%.2f%"),
                "Current Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                "Target Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                "Allocation Delta %": st.column_config.NumberColumn(format="%.2f%"),
                "CGT (Potential)": st.column_config.NumberColumn(format="PKR %.2f"),
                "Sharia Compliant": st.column_config.TextColumn(
                    "Sharia Compliant",
                    help="✅ = Sharia Compliant, ❌ = Non-Compliant"
                )
            },
            use_container_width=True
        )
        fig_pie = px.pie(
            portfolio_df,
            values='Total Invested',
            names='Stock',
            title='Portfolio Allocation (Based on Invested Amount)',
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No holdings in portfolio. Add transactions via 'Add Transaction'.")
