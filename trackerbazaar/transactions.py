import sqlite3
import pandas as pd
import streamlit as st
from datetime import date
from trackerbazaar.data import DB_FILE, init_db


class TransactionsUI:
    def __init__(self, user_email: str):
        self.user_email = user_email

    def _user_portfolios(self):
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name FROM portfolios WHERE owner_email=? ORDER BY name",
                (self.user_email,),
            )
            return cur.fetchall()

    def show(self):
        st.header("📜 Transactions")

        if not self.user_email:
            st.warning("Please log in to view/add transactions.")
            return

        init_db()
        portfolios = self._user_portfolios()
        if not portfolios:
            st.info("No portfolios yet. Create one in the **Portfolios** tab.")
            return

        name_by_id = {pid: name for pid, name in portfolios}
        selected_name = st.selectbox("Portfolio", [name for _, name in portfolios])
        portfolio_id = [pid for pid, nm in portfolios if nm == selected_name][0]

        # Add new transaction
        with st.form("add_tx"):
            c1, c2, c3 = st.columns(3)
            with c1:
                tx_date = st.date_input("Date", value=date.today())
                symbol = st.text_input("Symbol").upper().strip()
            with c2:
                tx_type = st.selectbox("Type", ["BUY", "SELL"])
                quantity = st.number_input("Quantity", min_value=1.0, step=1.0)
            with c3:
                price = st.number_input("Price (PKR)", min_value=0.0, step=1.0)
                fees = st.number_input("Fees (PKR)", min_value=0.0, step=1.0)
            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                if not symbol:
                    st.warning("Enter a symbol.")
                else:
                    try:
                        with sqlite3.connect(DB_FILE) as conn:
                            cur = conn.cursor()
                            cur.execute(
                                """INSERT INTO transactions
                                   (portfolio_id, date, symbol, type, quantity, price, fees)
                                   VALUES (?,?,?,?,?,?,?)""",
                                (portfolio_id, str(tx_date), symbol, tx_type, quantity, price, fees),
                            )
                            conn.commit()
                        st.success("Transaction added.")
                        try:
                            st.rerun()
                        except Exception:
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Failed to add transaction: {e}")

        # Transaction table
        with sqlite3.connect(DB_FILE) as conn:
            df = pd.read_sql_query(
                """SELECT date, symbol, type, quantity, price, fees
                   FROM transactions WHERE portfolio_id=? ORDER BY date DESC""",
                conn,
                params=(portfolio_id,),
            )

        st.subheader("History")
        if df.empty:
            st.info("No transactions yet.")
        else:
            st.dataframe(df, use_container_width=True)
