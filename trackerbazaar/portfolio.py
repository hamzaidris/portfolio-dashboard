import sqlite3
import streamlit as st
from trackerbazaar.data import DB_FILE, init_db

def list_portfolios():
    """Fetch all portfolios from DB"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, owner_email FROM portfolios")
        portfolios = cursor.fetchall()
    except Exception as e:
        portfolios = []
        st.error(f"Error loading portfolios: {e}")
    conn.close()
    return portfolios

def add_portfolio(name, owner_email):
    """Add a new portfolio to DB"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO portfolios (name, owner_email) VALUES (?, ?)",
            (name, owner_email),
        )
        conn.commit()
    except Exception as e:
        st.error(f"Error adding portfolio: {e}")
    finally:
        conn.close()

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
            st.write(f"**{p[1]}** (Owner: {p[2]})")

    st.subheader("➕ Add New Portfolio")
    with st.form("add_portfolio_form"):
        name = st.text_input("Portfolio Name")
        owner_email = st.text_input("Owner Email")
        submitted = st.form_submit_button("Add Portfolio")
        if submitted and name and owner_email:
            add_portfolio(name, owner_email)
            st.success(f"Portfolio '{name}' added!")

            # ✅ Compatible rerun
            try:
                st.rerun()  # New versions
            except Exception:
                st.experimental_rerun()  # Older versions
