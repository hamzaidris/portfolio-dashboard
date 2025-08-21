import streamlit as st
from trackerbazaar.users import UserManager  # Included for potential future use, but not used here
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.tracker import initialize_tracker
from trackerbazaar.add_transaction import render_add_transaction
from trackerbazaar.add_dividend import render_add_dividend  # Placeholder
from trackerbazaar.broker_fees import render_broker_fees  # Placeholder
from trackerbazaar.cash import render_cash
# Removed import of current_prices
from trackerbazaar.dashboard import render_dashboard
from trackerbazaar.data import render_data  # Placeholder
from trackerbazaar.distribution import render_distribution
from trackerbazaar.guide import render_guide
from trackerbazaar.notifications import render_notifications  # Placeholder
from trackerbazaar.portfolio import render_portfolio
from trackerbazaar.signup import render_signup  # Included but not used per your request
from trackerbazaar.stock_explorer import render_stock_explorer
from trackerbazaar.transactions import render_transactions  # Placeholder
from trackerbazaar.tracker import PortfolioTracker  # Utility, not a page

def main():
    st.set_page_config(layout="wide", page_title="Portfolio Dashboard", page_icon="📈")
    
    # Custom CSS for mobile-friendly design
    st.markdown("""
        <style>
        .stApp {
            max-width: 100%;
            margin: 0 auto;
            padding: 10px;
        }
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            flex: 1 1 auto;
            min-width: 120px;
            margin: 2px;
        }
        @media (max-width: 768px) {
            .stApp {
                padding: 5px;
            }
            .stTabs [data-baseweb="tab"] {
                min-width: 100px;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state for portfolios if not present
    if 'portfolios' not in st.session_state:
        st.session_state.portfolios = {}

    portfolio_manager = PortfolioManager()
    selected_portfolio = portfolio_manager.select_portfolio()
    if selected_portfolio is None:
        with st.form(key="create_portfolio_form"):
            portfolio_name = st.text_input("Enter Portfolio Name", key="new_portfolio_name")
            submit_button = st.form_submit_button("Create")
            if submit_button:
                if portfolio_name not in st.session_state.portfolios:
                    st.session_state.portfolios[portfolio_name] = {}
                    st.success(f"Portfolio '{portfolio_name}' created!")
                    # Automatically select the new portfolio and rerun
                    st.session_state.selected_portfolio = portfolio_name
                    st.rerun()
                else:
                    st.error("Portfolio name already exists!")
        st.stop()

    tracker = portfolio_manager.get_portfolio(selected_portfolio)
    if tracker is None:
        st.error("Tracker not found for selected portfolio.")
        st.stop()

    initialize_tracker(tracker)

    pages = {
        "Portfolio": render_portfolio,
        "Dashboard": render_dashboard,
        "Add Transaction": render_add_transaction,
        "Add Dividend": render_add_dividend,
        "Broker Fees": render_broker_fees,
        "Cash": render_cash,
        "Data": render_data,
        "Distribution": render_distribution,
        "Guide": render_guide,
        "Notifications": render_notifications,
        "Stock Explorer": render_stock_explorer,
        "Transactions": render_transactions
        # Excluded "Signup" per your request to exclude login/signup
    }
    page = st.sidebar.selectbox("Navigate", list(pages.keys()), key="nav_page")

    if page in pages:
        pages[page](tracker)

if __name__ == '__main__':
    main()
