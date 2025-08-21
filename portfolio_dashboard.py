import os
import streamlit as st

# Robust imports: prefer package, else local fallbacks
try:
    from trackerbazaar.dashboard import render_dashboard
    from trackerbazaar.portfolio import render_portfolio
    from trackerbazaar.distribution import render_distribution
    from trackerbazaar.cash import render_cash
    from trackerbazaar.stock_explorer import render_stock_explorer
    from trackerbazaar.notifications import render_notifications
    from trackerbazaar.transactions import render_transactions
    from trackerbazaar.current_prices import render_current_prices
    from trackerbazaar.add_transaction import render_add_transaction, render_sample_distribution
    from trackerbazaar.add_dividend import render_add_dividend
    from trackerbazaar.broker_fees import render_broker_fees
    from trackerbazaar.guide import render_guide
    from trackerbazaar.tracker import PortfolioTracker, initialize_tracker
    from trackerbazaar.users import UserManager
    from trackerbazaar.portfolios import PortfolioManager
except Exception as e:
    st.stop()

PROJECT_ROOT = os.path.dirname(__file__)

def main():
    st.set_page_config(page_title="TrackerBazaar - Portfolio Dashboard", layout="wide")
    st.title("📈 TrackerBazaar - Portfolio Dashboard")

    user_manager = UserManager()
    portfolio_manager = PortfolioManager()

    if not user_manager.is_logged_in():
        tabs = st.tabs(["Login", "Sign Up"])
        with tabs[0]:
            user_manager.login()
        with tabs[1]:
            user_manager.signup()
        st.info("Please log in or sign up to access your portfolios.")
        return

    st.sidebar.header("User")
    current_user = user_manager.get_current_user()
    current_username = user_manager.get_current_username()
    st.sidebar.write(f"Logged in as: {current_username} ({current_user})")
    user_manager.logout()

    st.sidebar.header("Portfolio Management")
    if "selected_portfolio" not in st.session_state:
        st.session_state.selected_portfolio = ""

    # Create or pick a portfolio
    new_portfolio_name = st.sidebar.text_input("New Portfolio Name", key="new_portfolio_name")
    if st.sidebar.button("Create Portfolio"):
        if not new_portfolio_name.strip():
            st.sidebar.error("Portfolio name cannot be empty.")
        else:
            tracker = portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
            st.session_state.selected_portfolio = new_portfolio_name.strip()
            st.success(f"Created portfolio '{new_portfolio_name}'.")

    # Existing portfolios
    names = portfolio_manager.list_portfolios(current_user)
    if names:
        sel = st.sidebar.selectbox(
            "Select Portfolio",
            options=names,
            index=max(0, names.index(st.session_state.selected_portfolio))
            if st.session_state.selected_portfolio in names else 0
        )
        st.session_state.selected_portfolio = sel

    # Load selected
    tracker = None
    if st.session_state.selected_portfolio:
        tracker = portfolio_manager.load_portfolio(st.session_state.selected_portfolio, current_user)

    if tracker is None:
        st.info("Create a portfolio to begin.")
        return

    # Ensure prices initialized
    initialize_tracker(tracker, project_root=PROJECT_ROOT)

    # Persist simple settings
    st.sidebar.header("Tax Settings")
    filer_status = st.sidebar.selectbox(
        "Filer Status",
        ["Filer", "Non-Filer"],
        index=0 if tracker.filer_status == "Filer" else 1
    )
    if filer_status != tracker.filer_status:
        tracker.update_filer_status(filer_status)
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, current_user, tracker)

    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
            "Dashboard", "Portfolio", "Distribution", "Cash",
            "Stock Explorer", "Notifications", "Transactions",
            "Current Prices", "Add Transaction", "Add Dividend",
            "Broker Fees", "Guide"
        ]
    )

    if page == "Dashboard":
        render_dashboard(tracker)
    elif page == "Portfolio":
        render_portfolio(tracker)
    elif page == "Distribution":
        render_distribution(tracker)
    elif page == "Cash":
        render_cash(tracker)
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, current_user, tracker)
    elif page == "Stock Explorer":
        render_stock_explorer(tracker)
    elif page == "Notifications":
        render_notifications(tracker)
    elif page == "Transactions":
        render_transactions(tracker)
    elif page == "Current Prices":
        render_current_prices(tracker)
    elif page == "Add Transaction":
        render_add_transaction(tracker)
        render_sample_distribution(tracker)
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, current_user, tracker)
    elif page == "Add Dividend":
        render_add_dividend(tracker)
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, current_user, tracker)
    elif page == "Broker Fees":
        render_broker_fees(tracker)
        portfolio_manager.save_portfolio(st.session_state.selected_portfolio, current_user, tracker)
    elif page == "Guide":
        render_guide()

if __name__ == "__main__":
    main()
