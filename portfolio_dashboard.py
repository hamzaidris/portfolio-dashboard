import streamlit as st
from trackerbazaar import (
    portfolio,
    dashboard,
    cash,
    add_transaction,
    add_dividend,
)
from trackerbazaar.user_manager import UserManager

def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")

    user_manager = UserManager()

    # Check login status
    if not user_manager.is_logged_in():
        st.title("🔐 Login to TrackerBazaar")
        user_manager.login_form()
        return  # Stop here if not logged in

    # If logged in, show navigation
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Go to", ["Portfolios", "Dashboard", "Cash", "Transactions", "Dividends", "Logout"])

    if page == "Portfolios":
        portfolio.show()
    elif page == "Dashboard":
        dashboard.show()
    elif page == "Cash":
        cash.show()
    elif page == "Transactions":
        add_transaction.show()
    elif page == "Dividends":
        add_dividend.show()
    elif page == "Logout":
        user_manager.logout()
        st.success("You have been logged out.")
        st.rerun()

if __name__ == "__main__":
    main()
