import streamlit as st
import sqlite3
from trackerbazaar.users import UserManager
from trackerbazaar.portfolios import PortfolioManager

DB_PATH = "trackerbazaar_v2.db"

# Ensure tables exist
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Create users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        # Create portfolios table
        c.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                data TEXT,
                FOREIGN KEY (email) REFERENCES users(email)
            )
        """)
        conn.commit()

def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")
    st.title("📊 TrackerBazaar – Portfolio Dashboard")

    # Init DB schema
    init_db()

    # Initialize managers
    user_manager = UserManager(DB_PATH)
    portfolio_manager = PortfolioManager(DB_PATH)

    # Initialize session vars
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "logged_in_username" not in st.session_state:
        st.session_state.logged_in_username = None

    current_user = st.session_state.logged_in_user

    # If not logged in → show login/signup
    if not current_user:
        st.subheader("Login / Signup")
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1:
            user_manager.login()
        with tab2:
            user_manager.signup()
        return

    # If logged in → show portfolio dashboard
    st.sidebar.write(f"Welcome, {st.session_state.logged_in_username or current_user} 👋")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None
        st.session_state.logged_in_username = None
        st.rerun()

    st.header("Your Portfolios")

    try:
        portfolios = portfolio_manager.list_portfolios(current_user)
        if portfolios:
            st.write("Available portfolios:", portfolios)
        else:
            st.info("No portfolios yet. Create one below.")
    except Exception as e:
        st.error(f"Database error while loading portfolios: {e}")

    st.subheader("Create New Portfolio")
    new_portfolio_name = st.text_input("Portfolio Name")
    if st.button("Create Portfolio"):
        if new_portfolio_name.strip():
            try:
                tracker = portfolio_manager.create_portfolio(new_portfolio_name.strip(), current_user)
                if tracker:
                    st.success(f"Portfolio '{new_portfolio_name}' created!")
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to create portfolio: {e}")
        else:
            st.warning("Please enter a portfolio name.")

if __name__ == "__main__":
    main()
