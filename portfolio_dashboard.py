# portfolio_dashboard.py

import streamlit as st

# App modules
from trackerbazaar.data import init_db
from trackerbazaar.user_manager import UserManager
from trackerbazaar.portfolio import PortfolioUI
from trackerbazaar.dashboard import DashboardUI
from trackerbazaar.cash import CashUI
from trackerbazaar.transactions import TransactionsUI
from trackerbazaar.dividends import DividendsUI


def main():
    # Configure page FIRST
    st.set_page_config(page_title="TrackerBazaar – Portfolio Dashboard", layout="wide")

    # Ensure DB schema exists (safe to call every run)
    try:
        init_db()
    except Exception as e:
        st.error(f"Database init failed: {e}")
        return

    # Auth
    um = UserManager()
    if not um.is_logged_in():
        st.title("🔐 Login to TrackerBazaar")
        um.login_form()
        return

    # Now it's safe to read session_state
    user_email = st.session_state.get("logged_in_user")

    # Sidebar navigation
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Portfolios", "Dashboard", "Cash", "Transactions", "Dividends", "Logout"],
        index=0,
    )

    if page == "Portfolios":
        PortfolioUI(user_email).show()
    elif page == "Dashboard":
        DashboardUI(user_email).show()
    elif page == "Cash":
        CashUI(user_email).show()
    elif page == "Transactions":
        TransactionsUI(user_email).show()
    elif page == "Dividends":
        DividendsUI(user_email).show()
    elif page == "Logout":
        um.logout()
        st.success("✅ Logged out")
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()


if __name__ == "__main__":
    main()
