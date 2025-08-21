import streamlit as st
import pandas as pd
import plotly.express as px
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.current_prices import get_current_price


def show_portfolio_ui(current_user):
    st.title("📊 Portfolio Overview")

    if not current_user:
        st.warning("Please log in to view your portfolio.")
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

    holdings = tracker.get_holdings()
    if not holdings:
        st.info("No holdings in this portfolio.")
        return

    # ---- Convert holdings to DataFrame ----
    data = []
    for ticker, info in holdings.items():
        avg_price = info["avg_price"]
        quantity = info["quantity"]
        invested = avg_price * quantity
        current_price = get_current_price(ticker) or avg_price  # fallback
        market_value = current_price * quantity
        pl = market_value - invested

        data.append({
            "Ticker": ticker,
            "Quantity": quantity,
            "Avg Buy Price": avg_price,
            "Invested (PKR)": invested,
            "Current Price": current_price,
            "Market Value (PKR)": market_value,
            "Profit/Loss (PKR)": pl
        })

    df = pd.DataFrame(data)

    # ---- Display portfolio table ----
    st.markdown("### Holdings")
    st.dataframe(df, use_container_width=True)

    # ---- Portfolio totals ----
    total_invested = df["Invested (PKR)"].sum()
    total_value = df["Market Value (PKR)"].sum()
    total_pl = df["Profit/Loss (PKR)"].sum()

    st.metric("💰 Total Invested", f"{total_invested:,.2f} PKR")
    st.metric("📈 Market Value", f"{total_value:,.2f} PKR")
    st.metric("📊 Total Profit/Loss", f"{total_pl:,.2f} PKR")

    # ---- Chart ----
    fig = px.bar(
        df,
        x="Ticker",
        y="Profit/Loss (PKR)",
        color="Profit/Loss (PKR)",
        title="Profit/Loss by Stock",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)
