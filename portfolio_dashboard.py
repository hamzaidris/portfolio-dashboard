import streamlit as st
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager


def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")
    st.title("📊 TrackerBazaar - Portfolio Dashboard")

    user_manager = UserManager()
    portfolio_manager = PortfolioManager()

    current_user = user_manager.get_current_user()

    if not current_user:
        # Show login/signup tabs
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            user_manager.login()
        with tab2:
            user_manager.signup()
        return

    # If logged in, show sidebar with username + logout
    st.sidebar.write(f"Welcome, {st.session_state.logged_in_username} 👋")
    user_manager.logout()

    # Portfolios section
    st.header("Your Portfolios")

    try:
        portfolios = portfolio_manager.list_portfolios(current_user)
        if portfolios:
            selected_portfolio = st.selectbox("Select a portfolio", portfolios)
            st.success(f"Loaded portfolio: {selected_portfolio}")
        else:
            st.info("No portfolios yet. Create one below!")
    except Exception as e:
        st.error(f"Database error while loading portfolios: {e}")
        portfolios = []

    # Create new portfolio
    new_portfolio_name = st.text_input("New Portfolio Name")
    if st.button("Create Portfolio"):
        if new_portfolio_name.strip():
            try:
                tracker = portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
                st.success(f"Portfolio '{new_portfolio_name}' created successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to create portfolio: {e}")
        else:
            st.warning("Please enter a portfolio name.")


if __name__ == "__main__":
    main()
