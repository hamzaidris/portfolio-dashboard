# dividends.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_dividends(selected_portfolio: str, user_email: str):
    """Dividend Manager — record and view dividends for a portfolio."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"💰 Dividend Manager — {selected_portfolio}")

    # ---- Add Dividend Form ----
    with st.form("add_dividend_form", clear_on_submit=True):
        st.markdown("### ➕ Add Dividend")

        col1, col2, col3 = st.columns(3)
        with col1:
            stock = st.text_input("Stock Symbol")
        with col2:
            amount = st.number_input("Dividend Amount (PKR)", min_value=0.0, step=0.01)
        with col3:
            date = st.date_input("Date")

        submitted = st.form_submit_button("💾 Save Dividend")

        if submitted:
            try:
                tracker.add_dividend({
                    "stock": stock.upper(),
                    "amount": amount,
                    "date": str(date)
                })
                portfolio_manager.save_portfolio(selected_portfolio, user_email, tracker)
                st.success(f"Dividend added: {amount} PKR for {stock}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add dividend: {e}")

    st.divider()

    # ---- Dividend History ----
    st.subheader("📑 Dividend History")
    if tracker.dividends:
        div_df = pd.DataFrame(tracker.dividends)

        div_df = div_df.rename(columns={
            "stock": "Stock",
            "amount": "Amount",
            "date": "Date"
        })

        st.dataframe(div_df, use_container_width=True)

        # ---- Total Dividends ----
        total_div = div_df["Amount"].sum()
        st.metric("Total Dividends (PKR)", f"{total_div:,.2f}")

        # ---- Chart of Dividends per Stock ----
        st.subheader("📊 Dividends by Stock")
        chart_df = div_df.groupby("Stock")["Amount"].sum().reset_index()
        st.bar_chart(chart_df.set_index("Stock"))

    else:
        st.info("No dividends recorded yet. Add one above ⬆️")
