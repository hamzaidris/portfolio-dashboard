# add_dividend.py
import streamlit as st
import pandas as pd
from trackerbazaar.portfolios import PortfolioManager

portfolio_manager = PortfolioManager()

def show_add_dividend(selected_portfolio: str, user_email: str):
    """Modern UI for adding and viewing dividends of a portfolio."""

    try:
        tracker = portfolio_manager.load_portfolio(selected_portfolio, user_email)
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
        return

    st.subheader(f"💰 Dividends — {selected_portfolio}")

    # ---- Add Dividend ----
    with st.expander("➕ Add Dividend", expanded=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            stock = st.text_input("Stock Symbol", placeholder="e.g., MCB")
        with col2:
            amount = st.number_input("Dividend Amount (PKR)", min_value=0.0, step=10.0)
        with col3:
            if st.button("Add Dividend", type="primary", use_container_width=True):
                try:
                    tracker.add_dividend(stock, amount)
                    portfolio_manager.save_portfolio(selected_portfolio, user_email, tracker)
                    st.success(f"Dividend of PKR {amount:,.2f} added for {stock} ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add dividend: {e}")

    st.divider()

    # ---- Dividend History ----
    if not tracker.dividends:
        st.info("No dividends recorded yet.")
    else:
        df = pd.DataFrame(tracker.dividends)
        st.dataframe(df, use_container_width=True)

        # ---- Dividend Summary ----
        total_dividends = df["amount"].sum()
        st.metric("Total Dividends Received", f"PKR {total_dividends:,.2f}")

        # ---- Grouped View ----
        grouped = df.groupby("stock")["amount"].sum().reset_index()
        st.bar_chart(grouped.set_index("stock"))

        # ---- Download Option ----
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Dividend History as CSV",
            data=csv,
            file_name=f"{selected_portfolio}_dividends.csv",
            mime="text/csv",
        )
