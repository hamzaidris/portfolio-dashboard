import streamlit as st
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager

user_manager = UserManager()
portfolio_manager = PortfolioManager()


def main():
    st.title("📊 TrackerBazaar")

    current_user = user_manager.get_current_user()

    if not current_user:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            user_manager.login()
        with tab2:
            user_manager.signup()
        return

    # Logged-in area
    st.sidebar.write(f"Welcome, {st.session_state.logged_in_username} 👋")
    user_manager.logout()

    # List user portfolios
    portfolios = portfolio_manager.list_portfolios(current_user)
    if portfolios:
        st.sidebar.subheader("Your Portfolios")
        for p in portfolios:
            st.sidebar.write(f"📁 {p}")
    else:
        st.sidebar.info("No portfolios yet. Create one below!")

    st.subheader("Create Portfolio")
    new_portfolio_name = st.text_input("Portfolio Name")
    if st.button("Create Portfolio"):
        if new_portfolio_name.strip():
            portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
            st.success(f"Portfolio '{new_portfolio_name}' created.")
            st.rerun()
        else:
            st.error("Enter a valid name.")


if __name__ == "__main__":
    main()
