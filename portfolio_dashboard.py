import streamlit as st
import json
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.tracker import Tracker

def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")
    st.title("📊 TrackerBazaar – Portfolio Dashboard")

    user_manager = UserManager()
    portfolio_manager = PortfolioManager()

    current_user = user_manager.get_current_user()

    if not current_user:
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1: user_manager.login()
        with tab2: user_manager.signup()
        return

    # Sidebar
    st.sidebar.write(f"Welcome, {st.session_state.logged_in_username} 👋")
    if st.sidebar.button("Logout"):
        user_manager.logout()
        st.rerun()

    # Portfolios
    st.subheader("Your Portfolios")

    try:
        portfolios = portfolio_manager.list_portfolios(current_user)
    except Exception as e:
        st.error(f"Database error while loading portfolios: {e}")
        portfolios = []

    portfolio_name = st.selectbox("Select Portfolio", portfolios) if portfolios else None

    with st.expander("Create New Portfolio"):
        new_portfolio_name = st.text_input("Portfolio Name")
        if st.button("Create Portfolio"):
            if new_portfolio_name.strip():
                try:
                    tracker = portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
                    st.success(f"Portfolio '{new_portfolio_name}' created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create portfolio: {e}")

    if not portfolio_name:
        st.info("Select or create a portfolio to continue.")
        return

    # Load portfolio data
    tracker = portfolio_manager.load_portfolio(portfolio_name, current_user)
    if not tracker:
        st.warning("Could not load portfolio data.")
        return

    # Main modules in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Trade Manager", "Dividends", "Cash", "Dashboard", "FIRE Tracker"]
    )

    with tab1:
        st.write("📑 Trade Manager")
        # render trade manager module here

    with tab2:
        st.write("💰 Dividends")
        # render dividends module here

    with tab3:
        st.write("🏦 Cash Movements")
        # render cash deposit/withdrawal entries

    with tab4:
        st.write("📊 Portfolio Dashboard")
        # charts + performance summary

    with tab5:
        st.write("🔥 FIRE Tracker")
        # financial independence goals

if __name__ == "__main__":
    main()
