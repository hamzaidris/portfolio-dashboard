import streamlit as st
import sqlite3
from trackerbazaar.data import DB_FILE

class PortfolioUI:
    def __init__(self, user_email):
        self.user_email = user_email

    def show(self):
        st.header("📂 Your Portfolios")

        if not self.user_email:
            st.warning("⚠️ Please log in to see your portfolios.")
            return

        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM portfolios WHERE owner_email=?", (self.user_email,))
                portfolios = cursor.fetchall()

            if portfolios:
                for (name,) in portfolios:
                    st.markdown(f"- **{name}**")
            else:
                st.info("No portfolios yet. Create one below 👇")
        except Exception as e:
            st.error(f"Error loading portfolios: {e}")

        # Add New Portfolio
        with st.form("new_portfolio"):
            portfolio_name = st.text_input("Portfolio Name")
            submitted = st.form_submit_button("➕ Add Portfolio")
            if submitted and portfolio_name:
                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO portfolios (name, owner_email) VALUES (?, ?)",
                            (portfolio_name, self.user_email)
                        )
                        conn.commit()
                    st.success(f"✅ Portfolio '{portfolio_name}' created.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding portfolio: {e}")
