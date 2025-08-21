import sqlite3
import pandas as pd
import streamlit as st
from datetime import date
from trackerbazaar.data import DB_FILE, init_db


class DividendsUI:
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
        st.header("💰 Dividends")

        if not self.user_email:
            st.warning("Please log in to manage dividends.")
            return

        init_db()
        portfolios = self._user_portfolios()
        if not portfolios:
            st.info("No portfolios yet. Create one in the **Portfolios** tab.")
            return

        selected_name = st.selectbox("Portfolio", [name for _, name in portfolios])
        portfolio_id = [pid for pid, nm in portfolios if nm == selected_name][0]

        # Add dividend
        with st.form("add_dividend"):
            c1, c2, c3 = st.columns(3)
            with c1:
                dv_date = st.date_input("Date", value=date.today())
            with c2:
                symbol = st.text_input("Symbol").upper().strip()
            with c3:
                amount = st.number_input("Amount (PKR)", min_value=0.0, step=1.0)

            submitted = st.form_submit_button("Add Dividend")
            if submitted:
                if not symbol:
                    st.warning("Enter a symbol.")
                else:
                    try:
                        with sqlite3.connect(DB_FILE) as conn:
                            cur = conn.cursor()
                            cur.execute(
                                """INSERT INTO dividends (portfolio_id, date, symbol, amount)
                                   VALUES (?,?,?,?)""",
                                (portfolio_id, str(dv_date), symbol, amount),
                            )
                            conn.commit()
                        st.success("Dividend added.")
                        try:
                            st.rerun()
                        except Exception:
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Failed to add dividend: {e}")

        # List dividends
        with sqlite3.connect(DB_FILE) as conn:
            df = pd.read_sql_query(
                """SELECT date, symbol, amount
                   FROM dividends WHERE portfolio_id=? ORDER BY date DESC""",
                conn,
                params=(portfolio_id,),
            )
        st.subheader("History")
        if df.empty:
            st.info("No dividends recorded.")
        else:
            st.dataframe(df, use_container_width=True)
