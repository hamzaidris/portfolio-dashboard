import sqlite3
import pandas as pd
import streamlit as st
from trackerbazaar.data import DB_FILE, init_db


class DashboardUI:
    def __init__(self, user_email: str):
        self.user_email = user_email

    def _get_user_portfolios(self):
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name FROM portfolios WHERE owner_email=? ORDER BY name",
                (self.user_email,),
            )
            return cur.fetchall()

    def _get_df(self, conn, sql, params=()):
        return pd.read_sql_query(sql, conn, params=params)

    def show(self):
        st.header("📊 Dashboard")

        if not self.user_email:
            st.warning("Please log in to view your dashboard.")
            return

        init_db()

        portfolios = self._get_user_portfolios()
        if not portfolios:
            st.info("No portfolios yet. Create one in the **Portfolios** tab.")
            return

        name_by_id = {pid: name for pid, name in portfolios}
        selected_name = st.selectbox("Portfolio", [name for _, name in portfolios])
        # map name back to id
        portfolio_id = [pid for pid, nm in portfolios if nm == selected_name][0]

        with sqlite3.connect(DB_FILE) as conn:
            tx = self._get_df(
                conn,
                """SELECT date, symbol, type, quantity, price, fees
                   FROM transactions WHERE portfolio_id=? ORDER BY date""",
                (portfolio_id,),
            )
            dv = self._get_df(
                conn,
                """SELECT date, symbol, amount
                   FROM dividends WHERE portfolio_id=? ORDER BY date""",
                (portfolio_id,),
            )
            cash = self._get_df(
                conn,
                """SELECT date, amount, COALESCE(note,'') AS note
                   FROM cash WHERE portfolio_id=? ORDER BY date""",
                (portfolio_id,),
            )

        # ---- Top metrics
        c1, c2, c3, c4 = st.columns(4)
        buys_val = (tx.query("type=='BUY'")["quantity"] * tx.query("type=='BUY'")["price"]).sum() if not tx.empty else 0.0
        sells_val = (tx.query("type=='SELL'")["quantity"] * tx.query("type=='SELL'")["price"]).sum() if not tx.empty else 0.0
        net_invested = buys_val - sells_val
        cash_balance = cash["amount"].sum() if not cash.empty else 0.0
        dividends_total = dv["amount"].sum() if not dv.empty else 0.0

        c1.metric("Portfolios", len(portfolios))
        c2.metric("Transactions", 0 if tx.empty else len(tx))
        c3.metric("Net Invested (PKR)", f"{net_invested:,.0f}")
        c4.metric("Cash Balance (PKR)", f"{cash_balance:,.0f}")

        st.caption(f"Dividends received: **PKR {dividends_total:,.0f}**")

        # ---- Holdings snapshot (net quantity + avg buy)
        st.subheader("Holdings (derived from transactions)")
        if tx.empty:
            st.info("No transactions yet.")
            return

        # net qty per symbol
        tx["qty_signed"] = tx.apply(
            lambda r: r["quantity"] if r["type"] == "BUY" else -r["quantity"], axis=1
        )
        net_qty = tx.groupby("symbol")["qty_signed"].sum()

        # weighted average buy price (on BUY rows only)
        buys = tx[tx["type"] == "BUY"].copy()
        if buys.empty:
            st.info("No BUY transactions to compute holdings.")
            return

        buys["notional"] = buys["quantity"] * buys["price"]
        wavg = (buys.groupby("symbol")["notional"].sum() /
                buys.groupby("symbol")["quantity"].sum())

        df = pd.DataFrame({
            "Symbol": net_qty.index,
            "Net Quantity": net_qty.values,
            "Avg Buy Price": wavg.reindex(net_qty.index).fillna(0).values,
        })
        df = df[df["Net Quantity"] > 0].sort_values("Symbol").reset_index(drop=True)

        if df.empty:
            st.info("No open positions at the moment.")
        else:
            df["Invested (PKR)"] = (df["Net Quantity"] * df["Avg Buy Price"]).round(2)
            st.dataframe(df, use_container_width=True)
