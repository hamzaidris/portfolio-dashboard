import streamlit as st
from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.tracker import initialize_tracker
from trackerbazaar.add_transaction import render_add_transaction
from trackerbazaar.cash import render_cash
from trackerbazaar.portfolio import render_portfolio
from trackerbazaar.dashboard import render_dashboard
from trackerbazaar.stock_explorer import render_stock_explorer
from trackerbazaar.guide import render_guide
from trackerbazaar.distribution import render_distribution

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

    portfolio_manager = PortfolioManager()
    selected_portfolio = portfolio_manager.select_portfolio()
    if selected_portfolio is None:
        with st.form(key="create_portfolio_form"):
            portfolio_name = st.text_input("Enter Portfolio Name", key="new_portfolio_name")
            submit_button = st.form_submit_button("Create")
            if submit_button:
                if portfolio_manager.create_portfolio(portfolio_name):
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
        "Cash": render_cash,
        "Stock Explorer": render_stock_explorer,
        "Guide": render_guide,
        "Distribution": render_distribution
    }
    page = st.sidebar.selectbox("Navigate", list(pages.keys()), key="nav_page")

    if page in pages:
        pages[page](tracker)

if __name__ == '__main__':
    main()
