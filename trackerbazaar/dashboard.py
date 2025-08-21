# dashboard.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_dashboard(selected_portfolio: str, user_email: str):
    """Modern Portfolio Dashboard"""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.title("📊 Portfolio Dashboard")

    # ---- Portfolio KPIs ----
    st.subheader(f"Overview — {selected_portfolio}")

    total_invested = tracker.get_total_invested()
    current_value = tracker.get_current_value()
    total_profit_loss = current_value - total_invested
    profit_loss_pct = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Invested", f"{total_invested:,.2f} PKR")
    col2.metric("📈 Current Value", f"{current_value:,.2f} PKR")
    col3.metric(
        "📊 P/L",
        f"{total_profit_loss:,.2f} PKR",
        delta=f"{profit_loss_pct:.2f}%" if total_invested > 0 else None,
    )
    col4.metric("📦 Holdings", f"{len(tracker.holdings)} stocks")

    st.divider()

    # ---- Holdings Table ----
    st.subheader("📑 Holdings")

    if tracker.holdings:
        holdings_df = pd.DataFrame(tracker.holdings).rename(columns={
            "symbol": "Symbol",
            "shares": "Shares",
            "avg_price": "Avg. Price",
            "current_price": "Current Price",
            "value": "Value",
            "profit_loss": "P/L"
        })

        holdings_df["P/L %"] = (
            (holdings_df["Current Price"] - holdings_df["Avg. Price"]) / holdings_df["Avg. Price"] * 100
        ).round(2)

        st.dataframe(holdings_df, use_container_width=True)

        # ---- Charts ----
        st.subheader("📊 Portfolio Distribution")

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Allocation by Value")
            st.bar_chart(
                holdings_df.set_index("Symbol")["Value"]
            )

        with col2:
            st.write("### Profit/Loss by Stock")
            st.bar_chart(
                holdings_df.set_index("Symbol")["P/L"]
            )

    else:
        st.info("No holdings yet. Add transactions to build your portfolio.")
