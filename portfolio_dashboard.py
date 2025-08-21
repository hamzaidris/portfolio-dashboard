# portfolio_dashboard.py
import streamlit as st
from trackerbazaar import (
    users,
    portfolios,
    transactions,
    dividends,
    cash,
    dashboard,
    stock_explorer,
    guide,
)

# ----------------------------
# Initialize Managers
# ----------------------------
user_manager = users.UserManager()
portfolio_manager = portfolios.PortfolioManager()

# ----------------------------
# Main App
# ----------------------------
def main():
    st.set_page_config(
        page_title="TrackerBazaar",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar: Authentication
    with st.sidebar:
        st.title("🔑 Account")
        if not user_manager.is_logged_in():
            choice = st.radio("Login / Signup", ["Login", "Signup"])
            if choice == "Login":
                user_manager.login()
            else:
                user_manager.signup()
            return
        else:
            st.success(f"Welcome, {st.session_state.logged_in_username} 👋")
            if st.button("Logout"):
                user_manager.logout()
                st.rerun()

    # Sidebar: Portfolio selection
    current_user = user_manager.get_current_user()
    portfolios_list = portfolio_manager.list_portfolios(current_user)

    with st.sidebar:
        st.title("📂 Portfolios")
        if portfolios_list:
            selected_portfolio = st.selectbox(
                "Select Portfolio", portfolios_list, index=0
            )
            st.session_state.selected_portfolio = selected_portfolio
        else:
            st.info("No portfolios yet. Create one below.")
            st.session_state.selected_portfolio = None

        new_name = st.text_input("➕ New Portfolio Name")
        if st.button("Create Portfolio"):
            if new_name.strip():
                try:
                    portfolio_manager.create_portfolio(new_name.strip(), current_user)
                    st.success(f"Portfolio '{new_name}' created.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create portfolio: {e}")
            else:
                st.warning("Enter a valid name!")

    # Main content: Tabs
    st.title("📊 TrackerBazaar")

    if not st.session_state.selected_portfolio:
        st.info("Select or create a portfolio to get started.")
        return

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "🏠 Dashboard",
            "💹 Transactions",
            "💰 Dividends",
            "💵 Cash",
            "🔎 Stock Explorer",
            "📘 Guide",
            "⚙️ Settings",
        ]
    )

    with tab1:
        dashboard.show_dashboard(st.session_state.selected_portfolio, current_user)

    with tab2:
        transactions.show_transactions(st.session_state.selected_portfolio, current_user)

    with tab3:
        dividends.show_dividends(st.session_state.selected_portfolio, current_user)

    with tab4:
        cash.show_cash(st.session_state.selected_portfolio, current_user)

    with tab5:
        stock_explorer.show_stock_explorer()

    with tab6:
        guide.show_guide()

    with tab7:
        st.subheader("⚙️ Settings")
        st.write("Manage your account and portfolios here.")
        if st.button("Delete Selected Portfolio"):
            try:
                portfolio_manager.delete_portfolio(
                    st.session_state.selected_portfolio, current_user
                )
                st.success("Portfolio deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete: {e}")


if __name__ == "__main__":
    main()
