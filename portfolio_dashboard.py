import streamlit as st
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager

user_manager = UserManager()
portfolio_manager = PortfolioManager()

def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")
    st.title("📊 TrackerBazaar")

    current_user = user_manager.get_current_user()

    if not current_user:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1: user_manager.login()
        with tab2: user_manager.signup()
        return

    # Sidebar
    st.sidebar.write(f"Welcome, {st.session_state.logged_in_username} 👋")
    if st.sidebar.button("Logout"):
        user_manager.logout()

    # Portfolio section
    st.header("Your Portfolios")
    portfolios = portfolio_manager.list_portfolios(current_user)

    if not portfolios:
        st.info("No portfolios found. Create one below.")
    else:
        choice = st.selectbox("Select portfolio", portfolios)
        if choice:
            tracker = portfolio_manager.load_portfolio(choice, current_user)
            st.success(f"Loaded portfolio: {choice}")
            st.write(tracker.__dict__)

    with st.form("create_portfolio_form"):
        new_name = st.text_input("New Portfolio Name")
        create = st.form_submit_button("Create")
        if create and new_name.strip():
            tracker = portfolio_manager.create_portfolio(new_name.strip(), current_user)
            st.success(f"Portfolio '{new_name}' created.")
            st.experimental_rerun()

if __name__ == "__main__":
    main()
