import streamlit as st
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager

# Initialize managers
user_manager = UserManager()
portfolio_manager = PortfolioManager()


def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")

    # Sidebar login/signup
    st.sidebar.title("User Authentication")
    tab1, tab2 = st.sidebar.tabs(["Login", "Sign Up"])

    with tab1:
        user_manager.login()
    with tab2:
        user_manager.signup()

    current_user = user_manager.get_current_user()

    if not current_user:
        st.info("👈 Please log in to continue.")
        return

    # After login
    st.sidebar.success(f"Welcome, {st.session_state.get('logged_in_username', 'User')} 👋")

    st.title("📊 TrackerBazaar Dashboard")

    # Portfolio section
    st.header("Your Portfolios")

    try:
        portfolios = portfolio_manager.list_portfolios(current_user)
    except Exception as e:
        st.error(f"Database error while loading portfolios: {e}")
        portfolios = []

    if portfolios:
        selected_portfolio = st.selectbox("Select a portfolio", portfolios)
        if selected_portfolio:
            tracker = portfolio_manager.load_portfolio(selected_portfolio, current_user)
            st.write(f"✅ Loaded portfolio: **{selected_portfolio}**")
            st.json(tracker.to_dict())
    else:
        st.info("No portfolios found. Create one below 👇")

    # Create new portfolio
    with st.form("create_portfolio_form", clear_on_submit=True):
        new_name = st.text_input("New Portfolio Name")
        submitted = st.form_submit_button("Create Portfolio")
        if submitted and new_name.strip():
            try:
                tracker = portfolio_manager.create_portfolio(new_name.strip(), current_user)
                st.success(f"Portfolio **{new_name.strip()}** created!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to create portfolio: {e}")


if __name__ == "__main__":
    main()
