import streamlit as st
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager

user_manager = UserManager()
portfolio_manager = PortfolioManager()

def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")

    st.title("📊 TrackerBazaar - Portfolio Manager")

    if not st.session_state.logged_in_user:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            user_manager.login()
        with tab2:
            user_manager.signup()
        return

    # Sidebar welcome
    st.sidebar.write(f"Welcome, {st.session_state.logged_in_username} 👋")
    if st.sidebar.button("Logout"):
        user_manager.logout()

    # Portfolio section
    st.header("Your Portfolios")
    current_user = st.session_state.logged_in_user

    portfolios = portfolio_manager.list_portfolios(current_user)
    if portfolios:
        selected = st.selectbox("Select Portfolio", portfolios)
        st.write(f"📂 Loaded portfolio: {selected}")
    else:
        st.info("No portfolios yet. Create one below!")

    new_portfolio_name = st.text_input("New Portfolio Name")
    if st.button("Create Portfolio"):
        if new_portfolio_name.strip():
            portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
            st.success(f"Portfolio '{new_portfolio_name}' created!")
            st.rerun()
        else:
            st.error("Please enter a portfolio name.")

if __name__ == "__main__":
    main()
