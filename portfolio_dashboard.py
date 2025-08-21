# portfolio_dashboard.py
import streamlit as st
from trackerbazaar import (
    portfolio,
    dashboard,
    add_transaction,
    add_dividend,
    cash,
    admin_tools,  # ✅ new import
)

def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")

    st.sidebar.title("📊 TrackerBazaar")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Portfolio", "Dashboard", "Transactions", "Dividends", "Cash", "Admin Tools"]
    )

    if page == "Portfolio":
        portfolio.show()
    elif page == "Dashboard":
        dashboard.show()
    elif page == "Transactions":
        add_transaction.show()
    elif page == "Dividends":
        add_dividend.show()
    elif page == "Cash":
        cash.show()
    elif page == "Admin Tools":
        admin_tools.show_admin_tools()

if __name__ == "__main__":
    main()
