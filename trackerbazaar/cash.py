import streamlit as st
import sqlite3
from datetime import datetime

DB_FILE = "trackerbazaar_v2.db"  # ✅ New database file

def init_cash_table():
    """Ensure cash table exists."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS cash (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT CHECK(type IN ('deposit','withdrawal')) NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()

def add_cash_transaction(email, amount, tx_type):
    """Insert a cash transaction (deposit or withdrawal)."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO cash (email, amount, type, timestamp) VALUES (?,?,?,?)",
            (email, amount, tx_type, datetime.now().isoformat())
        )
        conn.commit()

def get_cash_balance(email):
    """Calculate current cash balance for a user."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT SUM(CASE WHEN type='deposit' THEN amount ELSE -amount END) FROM cash WHERE email=?", (email,))
        result = c.fetchone()
        return result[0] if result and result[0] else 0.0

def view_cash_module(email):
    """Render Cash Manager UI."""
    st.markdown("## 💵 Cash Manager")

    # Current balance card
    balance = get_cash_balance(email)
    st.markdown(
        f"""
        <div style="padding:1rem; border-radius:12px; background:linear-gradient(135deg,#1e3c72,#2a5298); color:white; text-align:center; margin-bottom:1rem;">
            <h3 style="margin:0;">Current Balance</h3>
            <p style="font-size:1.5rem; font-weight:bold; margin:0;">{balance:,.2f} PKR</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabs for actions
    tab1, tab2 = st.tabs(["➕ Deposit", "➖ Withdraw"])

    with tab1:
        with st.form("deposit_form", clear_on_submit=True):
            deposit_amount = st.number_input("Enter deposit amount", min_value=0.0, step=100.0, format="%.2f")
            if st.form_submit_button("Add Deposit", use_container_width=True):
                if deposit_amount > 0:
                    add_cash_transaction(email, deposit_amount, "deposit")
                    st.success(f"Deposited {deposit_amount:,.2f} PKR ✅")
                    st.rerun()
                else:
                    st.warning("Amount must be greater than 0")

    with tab2:
        with st.form("withdraw_form", clear_on_submit=True):
            withdraw_amount = st.number_input("Enter withdrawal amount", min_value=0.0, step=100.0, format="%.2f")
            if st.form_submit_button("Withdraw", use_container_width=True):
                if withdraw_amount > 0:
                    if withdraw_amount <= balance:
                        add_cash_transaction(email, withdraw_amount, "withdrawal")
                        st.success(f"Withdrew {withdraw_amount:,.2f} PKR ✅")
                        st.rerun()
                    else:
                        st.error("Insufficient balance ❌")
                else:
                    st.warning("Amount must be greater than 0")

    # Transaction history
    st.markdown("### 📜 Transaction History")
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT amount, type, timestamp FROM cash WHERE email=? ORDER BY id DESC", (email,))
        rows = c.fetchall()

    if rows:
        st.dataframe(
            [{"Amount": r[0], "Type": r[1].capitalize(), "Date": r[2][:19]} for r in rows],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No transactions yet. Add a deposit or withdrawal to get started.")

# Initialize DB table on import
init_cash_table()
