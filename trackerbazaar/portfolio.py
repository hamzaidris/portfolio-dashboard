# trackerbazaar/portfolio.py
import sqlite3
import streamlit as st
from trackerbazaar.data import DB_FILE, init_db

class PortfolioUI:
    def __init__(self, user_email: str):
        self.user_email = user_email

    def list_portfolios(self):
        """Fetch portfolios belonging to the logged-in user"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name FROM portfolios WHERE owner_email=?",
                (self.user_email,)
            )
            return cursor.fetchall()

    def add_portfolio(self, name: str):
        """Add a new portfolio for the current user"""
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO portfolios (name, owner_email) VALUES (?, ?)",
                (name, self.user_email)
            )
            conn.commit()

    def show(self):
        """Streamlit UI for portfolio management"""
        st.header("📂 Your Portfolios")

        if not self.user_email:
            st.warning("⚠️ Please log in to manage portfolios.")
            return

        # Ensure schema is ready
        init_db()

        # Display portfolios
        portfolios = self.list_portfolios()
        if not portfolios:
            st.info("No portfolios found. Create one below 👇")
        else:
            for pid, name in portfolios:
                st.markdown(f"- **{name}** (ID: {pid})")

        # Add new portfolio form
        st.subheader("➕ Add New Portfolio")
        with st.form("add_portfolio_form"):
            portfolio_name = st.text_input("Portfolio Name")
            submitted = st.form_submit_button("Add Portfolio")

            if submitted:
                if not portfolio_name.strip():
                    st.warning("⚠️ Please enter a portfolio name.")
                else:
                    try:
                        self.add_portfolio(portfolio_name.strip())
                        st.success(f"✅ Portfolio '{portfolio_name}' created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to create portfolio: {e}")
