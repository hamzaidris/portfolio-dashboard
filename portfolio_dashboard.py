import streamlit as st
from trackerbazaar import (
    users,
    signup,
    portfolios,
    transactions,
    add_transaction,
    add_dividend,
    dividends,
    cash,
    broker_fees,
    current_prices,
    distribution,
    dashboard,
    stock_explorer,
    guide,
    notifications,
)
import os

DB_FILE = "trackerbazaar_v2.db"  # ✅ always use the new db file


# ------------------- APP ENTRY -------------------
def main():
    st.set_page_config(
        page_title="TrackerBazaar",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Title bar
    st.title("📊 TrackerBazaar")
    st.caption("Personal Portfolio Tracker with Modern UI")

    # Session state setup
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "logged_in_username" not in st.session_state:
        st.session_state.logged_in_username = None

    # If not logged in → show login/signup tabs
    if not st.session_state.logged_in_user:
        tab_login, tab_signup = st.tabs(["🔑 Login", "🆕 Sign Up"])
        with tab_login:
            users.login(DB_FILE)
        with tab_signup:
            signup.signup(DB_FILE)
        return

    # ------------------- SIDEBAR -------------------
    st.sidebar.image("https://img.icons8.com/color/96/000000/investment-portfolio.png", width=100)
    st.sidebar.write(f"👋 Welcome, **{st.session_state.logged_in_username}**")

    menu = st.sidebar.radio(
        "📂 Navigation",
        [
            "📁 Portfolio Manager",
            "💸 Transactions",
            "🏦 Dividends",
            "💰 Cash",
            "📈 Dashboard",
            "📊 Stock Explorer",
            "📚 Guide",
            "🔔 Notifications",
        ],
    )

    # ------------------- MAIN CONTENT -------------------
    if menu == "📁 Portfolio Manager":
        portfolios.portfolio_manager_ui(DB_FILE)

    elif menu == "💸 Transactions":
        tab1, tab2 = st.tabs(["➕ Add Transaction", "📜 All Transactions"])
        with tab1:
            add_transaction.add_transaction_ui(DB_FILE)
        with tab2:
            transactions.transactions_ui(DB_FILE)

    elif menu == "🏦 Dividends":
        tab1, tab2 = st.tabs(["➕ Add Dividend", "📜 Dividend History"])
        with tab1:
            add_dividend.add_dividend_ui(DB_FILE)
        with tab2:
            dividends.dividends_ui(DB_FILE)

    elif menu == "💰 Cash":
        cash.cash_ui(DB_FILE)

    elif menu == "📈 Dashboard":
        dashboard.dashboard_ui(DB_FILE)

    elif menu == "📊 Stock Explorer":
        stock_explorer.stock_explorer_ui()

    elif menu == "📚 Guide":
        guide.guide_ui()

    elif menu == "🔔 Notifications":
        notifications.notifications_ui(DB_FILE)

    # ------------------- FOOTER -------------------
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in_user = None
        st.session_state.logged_in_username = None
        st.rerun()


if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        st.warning(f"Database not found → Creating `{DB_FILE}`...")
        # Each module should auto-init its tables when first run
    main()
