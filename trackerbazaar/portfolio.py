# trackerbazaar/portfolio.py
import streamlit as st
import sqlite3
from trackerbazaar.data import DB_FILE, init_db

def list_portfolios():
    """Fetch all portfolios from DB"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, owner_email, created_at FROM portfolios")
        portfolios = cursor.fetchall()
    except Exception as e:
        portfolios = []
        st.error(f"Error loading portfolios: {e}")
    conn.close()
    return portfolios

def show():
    """Streamlit UI for managing portfolios"""
    st.header("📂 Your Portfolios")

    # Ensure DB exists
    init_db()

    portfolios = list_portfolios()
    if not portfolios:
        st.info("No portfolios found. Add one below.")
    else:
        for p in portfolios:
            st.write(f"**{p[1]}** (Owner: {p[2]}, Created: {p[3]})")

    # Form to add portfolio
    st.subheader("➕ Add New Portfolio")
    with st.form("add_portfolio_form"):
        name = st.text_input("Portfolio Name")
        owner_email = st.text_input("Owner Email")
        submitted = st.form_submit_button("Create Portfolio")

        if submitted:
            if not name or not owner_email:
                st.warning("⚠️ Please enter both name and email.")
            else:
                try:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO portfolios (name, owner_email) VALUES (?, ?)",
                        (name, owner_email)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Portfolio '{name}' created!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Failed to create portfolio: {e}")
