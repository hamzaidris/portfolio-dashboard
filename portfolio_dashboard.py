import streamlit as st
from trackerbazaar.tracker import PortfolioTracker, initialize_tracker
from trackerbazaar.portfolio import render_portfolio
from trackerbazaar.cash import render_cash
from trackerbazaar.add_transaction import render_add_transaction
from trackerbazaar.add_dividend import render_add_dividend
from trackerbazaar.notifications import render_notifications
from trackerbazaar.dashboard import render_dashboard
from trackerbazaar.transactions import render_transactions
from trackerbazaar.portfolios import PortfolioManager

# Assume an auth module exists
from trackerbazaar.auth import login_user  # Replace with your actual auth module

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['tracker'] = None
        st.session_state['portfolio_name'] = None

    # Check if user is logged in
    if not st.session_state['logged_in']:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user_data = login_user(username, password)  # Returns {'username': str, 'email': str} or None
            if user_data:
                st.session_state['logged_in'] = True
                st.session_state['user'] = user_data
                st.session_state['tracker'] = PortfolioTracker()
                initialize_tracker(st.session_state['tracker'])
                st.success(f"Logged in as {user_data['username']}")
                st.rerun()  # Refresh to show main app
            else:
                st.error("Invalid credentials")
        return

    # User is logged in
    user = st.session_state['user']
    tracker = st.session_state['tracker']
    portfolio_manager = PortfolioManager()

    # Display user info and logout button
    st.sidebar.write(f"Logged in as: {user['username']} ({user['email']})")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['tracker'] = None
        st.session_state['portfolio_name'] = None
        st.rerun()  # Refresh to show login page

    # Portfolio selection
    portfolios = portfolio_manager.list_portfolios()
    portfolio_name = st.sidebar.selectbox("Select Portfolio", [""] + portfolios)
    if portfolio_name:
        st.session_state['portfolio_name'] = portfolio_name
        portfolio_data = portfolio_manager.load_portfolio(portfolio_name)
        if portfolio_data:
            tracker.__dict__.update(portfolio_data)

    # Navigation
    page = st.sidebar.selectbox("Navigate", [
        "Dashboard",
        "Portfolio",
        "Cash Management",
        "Add Transaction",
        "Transaction History",
        "Add Dividend",
        "Notifications"
    ])

    # Render selected page
    if page == "Dashboard":
        render_dashboard(tracker)
    elif page == "Portfolio":
        render_portfolio(tracker)
    elif page == "Cash Management":
        render_cash(tracker)
    elif page == "Add Transaction":
        render_add_transaction(tracker)
    elif page == "Transaction History":
        render_transactions(tracker)
    elif page == "Add Dividend":
        render_add_dividend(tracker)
    elif page == "Notifications":
        render_notifications(tracker)

    # Save portfolio state
    if st.session_state['portfolio_name']:
        portfolio_manager.save_portfolio(st.session_state['portfolio_name'], tracker.__dict__)

if __name__ == "__main__":
    main()
