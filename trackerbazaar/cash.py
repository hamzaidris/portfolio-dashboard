import sqlite3
import pandas as pd
import streamlit as st
from datetime import date
from trackerbazaar.data import DB_FILE, init_db


class CashUI:
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
        st.header("💵 Cash")

        if not self.user_email:
            st.warning("Please log in to manage cash.")
            return

        init_db()
        portfolios = self._user_portfolios()
        if not portfolios:
            st.info("No portfolios yet. Create one in the **Portfolios** tab.")
            return

        selected_name = st.selectbox("Portfolio", [name for _, name in portfolios])
        portfolio_id = [pid for pid, nm in portfolios if nm == selected_name][0]

        # Add cash record
        with st.form("add_cash"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cash_date = st.date_input("Date", value=date.today())
            with c2:
                kind = st.radio("Type", ["Deposit", "Withdraw"], horizontal=True)
            with c3:
                amount = st.number_input("Amount (PKR)", min_value=0.0, step=1.0)
            note = st.text_input("Note (optional)")

            submitted = st.form_submit_button("Save")
            if submitted:
                signed_amount = amount if kind == "Deposit" else -amount
                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        cur = conn.cursor()
                        cur.execute(
                            """INSERT INTO cash (portfolio_id, date, amount, note)
                               VALUES (?,?,?,?)""",
                            (portfolio_id, str(cash_date), signed_amount, note),
                        )
                        conn.commit()
                    st.success("Cash record saved.")
                    try:
                        st.rerun()
                    except Exception:
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Failed to save cash record: {e}")

        # List cash
        with sqlite3.connect(DB_FILE) as conn:
            df = pd.read_sql_query(
                """SELECT date, amount, COALESCE(note,'') AS note
                   FROM cash WHERE portfolio_id=? ORDER BY date DESC""",
                conn,
                params=(portfolio_id,),
            )
        st.subheader("History")
        if df.empty:
            st.info("No cash records yet.")
        else:
            st.dataframe(df, use_container_width=True)
            st.caption(f"Balance: **PKR {df['amount'].sum():,.0f}**")
