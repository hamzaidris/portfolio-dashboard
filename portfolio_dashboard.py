import streamlit as st
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.tracker import Tracker

# Initialize managers
user_manager = UserManager()
portfolio_manager = PortfolioManager()


def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")
    st.title("📊 TrackerBazaar")

    # Sidebar login / signup
    if not st.session_state.get("logged_in_user"):
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            user_manager.login()
        with tab2:
            user_manager.signup()
        return

    # Logged in
    current_user = st.session_state.logged_in_user
    st.sidebar.success(f"Welcome, {st.session_state.get('logged_in_username', current_user)} 👋")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None
        st.session_state.logged_in_username = None
        st.experimental_rerun()

    st.header("Your Portfolios")

    # Load user portfolios
    try:
        portfolios = portfolio_manager.list_portfolios(current_user)
    except Exception as e:
        st.error(f"Database error while loading portfolios: {e}")
        portfolios = []

    # Select existing portfolio
    selected_portfolio = None
    if portfolios:
        selected_name = st.selectbox("Select Portfolio", portfolios)
        if selected_name:
            try:
                selected_portfolio = portfolio_manager.load_portfolio(selected_name, current_user)
                st.success(f"Loaded portfolio: {selected_name}")
            except Exception as e:
                st.error(f"Error loading portfolio {selected_name}: {e}")

    # Create new portfolio
    st.subheader("Create New Portfolio")
    new_portfolio_name = st.text_input("Portfolio Name")
    if st.button("Create Portfolio"):
        if not new_portfolio_name.strip():
            st.warning("Please enter a valid portfolio name.")
        else:
            try:
                tracker = portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
                st.success(f"Portfolio '{new_portfolio_name}' created successfully.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to create portfolio: {e}")

    # Show tracker content if portfolio selected
    if selected_portfolio:
        st.subheader("Portfolio Overview")
        st.write("Transactions:", selected_portfolio.transactions)
        st.write("Dividends:", selected_portfolio.dividends)
        st.write("Cash Balance:", selected_portfolio.cash_balance)


if __name__ == "__main__":
    main()
