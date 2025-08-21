import streamlit as st
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager

user_manager = UserManager()
portfolio_manager = PortfolioManager()

def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")

    # Sidebar greeting
    if st.session_state.get("logged_in_user"):
        st.sidebar.write(f"Welcome, {st.session_state.get('logged_in_username', '')} 👋")
        current_user = st.session_state.logged_in_user
    else:
        st.sidebar.write("Please log in")
        current_user = None

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Login / Signup", "Portfolios", "Dashboard"])

    with tab1:
        user_manager.login()
        user_manager.signup()

    with tab2:
        if current_user:
            st.subheader("Your Portfolios")
            portfolios = portfolio_manager.list_portfolios(current_user)
            if portfolios:
                st.write("Available Portfolios:", portfolios)
            else:
                st.info("No portfolios yet. Create one below:")

            new_portfolio_name = st.text_input("New Portfolio Name")
            if st.button("Create Portfolio") and new_portfolio_name.strip():
                tracker = portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
                st.success(f"Portfolio '{new_portfolio_name}' created!")
        else:
            st.warning("Please log in to manage portfolios.")

    with tab3:
        st.subheader("Dashboard (Coming Soon)")

if __name__ == "__main__":
    main()
