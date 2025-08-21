import streamlit as st

from trackerbazaar import (
    add_transaction,
    add_dividend,
    broker_fees,
    cash,
    current_prices,
    dashboard,
    data,
    distribution,
    guide,
    notifications,
    portfolio,
    portfolios,
    stock_explorer,
    transactions,
    users,
)

from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.users import UserManager


def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")
    st.title("📊 TrackerBazaar — Portfolio Dashboard")

    user_manager = UserManager()
    portfolio_manager = PortfolioManager()

    if not user_manager.get_current_user():
        st.info("Please login or sign up to continue.")
        user_manager.login_signup_panel()
        return

    current_user = user_manager.get_current_user()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = {
        "Dashboard": dashboard,
        "Transactions": transactions,
        "Dividends": add_dividend,
        "Add Transaction": add_transaction,
        "Cash Management": cash,
        "Stock Explorer": stock_explorer,
        "Portfolio": portfolio,
        "Broker Fees": broker_fees,
        "Distribution": distribution,
        "Guide": guide,
        "Notifications": notifications,
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    # Portfolios section
    st.sidebar.subheader("Your Portfolios")
    try:
        portfolios_list = portfolio_manager.list_portfolios(current_user)
        if portfolios_list:
            for p in portfolios_list:
                st.sidebar.write(f"📂 {p}")
        else:
            st.sidebar.write("No portfolios yet.")
    except Exception as e:
        st.sidebar.error(f"Error loading portfolios: {e}")

    # Page rendering
    page = pages[choice]
    if hasattr(page, "app"):
        page.app()
    else:
        st.warning("This section is under construction.")


if __name__ == "__main__":
    main()
