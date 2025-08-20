import streamlit as st
import pandas as pd
import plotly.express as px
from .tracker import PortfolioTracker

def render_dashboard(tracker):
    st.header("Dashboard")
    dashboard = tracker.get_dashboard()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Portfolio Value", f"PKR {dashboard['Total Portfolio Value']:,.2f}")
    col2.metric("Total ROI %", f"{dashboard['Total ROI %']:.2f}%")
    col3.metric("Total Dividends", f"PKR {dashboard['Total Dividends']:,.2f}")
    col4.metric("Cash Balance", f"PKR {tracker.cash:,.2f}")
    col1.metric("Total Invested", f"PKR {dashboard['Total Invested']:,.2f}")
    col2.metric("Total Realized Gain", f"PKR {dashboard['Total Realized Gain']:,.2f}")
    col3.metric("Total Unrealized Gain", f"PKR {dashboard['Total Unrealized Gain']:,.2f}")
    col4.metric("% of Target Invested", f"{dashboard['% of Target Invested']:.2f}%")

    portfolio_df = tracker.get_portfolio()
    if not portfolio_df.empty:
        fig_bar = px.bar(
            portfolio_df,
            x='Stock',
            y=['Market Value', 'Gain/Loss'],
            title='Portfolio Value and Gains/Losses by Asset',
            barmode='group',
            color_discrete_map={'Market Value': '#636EFA', 'Gain/Loss': '#EF553B'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_alloc = px.bar(
            portfolio_df,
            x='Stock',
            y=['Current Allocation %', 'Target Allocation %'],
            title='Current vs Target Allocation',
            barmode='group',
            color_discrete_map={'Current Allocation %': '#636EFA', 'Target Allocation %': '#00CC96'}
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

        invested_df = tracker.get_invested_timeline()
        if not invested_df.empty:
            fig_invested = px.line(
                invested_df,
                x='date',
                y='invested',
                title='Amount Invested Over Time'
            )
            st.plotly_chart(fig_invested, use_container_width=True)

        pl_df = tracker.get_profit_loss_timeline()
        if not pl_df.empty:
            fig_pl = px.line(
                pl_df,
                x='date',
                y='profit_loss',
                title='Profit/Loss Over Time (Approximate)'
            )
            st.plotly_chart(fig_pl, use_container_width=True)
        else:
            st.info("Historical profit/loss data not available.")
    else:
        st.info("Your portfolio is empty. Add transactions to get started.")
