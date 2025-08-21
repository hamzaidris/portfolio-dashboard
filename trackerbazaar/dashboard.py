# trackerbazaar/dashboard.py

import sqlite3
import pandas as pd
import streamlit as st
from trackerbazaar.data import DB_FILE, init_db


class DashboardUI:
    def __init__(self, user_email: str):
        self.user_email = user_email

    # ------------------------- helpers -------------------------

    def _get_user_portfolios(self):
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name FROM portfolios WHERE owner_email=? ORDER BY name",
                (self.user_email,),
            )
            return cur.fetchall()

    def _safe_tx_df(self, conn, portfolio_id: int) -> pd.DataFrame:
        """
        Load transactions for the portfolio and normalize columns so the rest
        of the code can rely on: date, symbol, type, quantity, price, fees.
        Works with old schemas (ticker/transaction_type/brokerage) too.
        """
        try:
            # Preferred (new) schema
            df = pd.read_sql_query(
                """SELECT date, symbol, type, quantity, price, fees
                   FROM transactions WHERE portfolio_id=? ORDER BY date""",
                conn,
                params=(portfolio_id,),
            )
            return df
        except Exception:
            # Fallback: load everything and remap columns
            df = pd.read_sql_query(
                "SELECT * FROM transactions WHERE portfolio_id=? ORDER BY date",
                conn,
                params=(portfolio_id,),
            )

            # symbol vs ticker
            if "symbol" not in df.columns and "ticker" in df.columns:
                df["symbol"] = df["ticker"]
            elif "symbol" not in df.columns:
                df["symbol"] = ""

            # type vs transaction_type
            if "type" not in df.columns and "transaction_type" in df.columns:
                df["type"] = df["transaction_type"]
            elif "type" not in df.columns:
                df["type"] = ""

            # fees vs brokerage
            if "fees" not in df.columns and "brokerage" in df.columns:
                df["fees"] = df["brokerage"]
            elif "fees" not in df.columns:
                df["fees"] = 0.0

            # Ensure required numeric cols exist
            for col in ("quantity", "price", "fees"):
                if col not in df.columns:
                    df[col] = 0.0

            if "date" not in df.columns:
                df["date"] = ""

            # Keep only what we need in the expected order
            return df[["date", "symbol", "type", "quantity", "price", "fees"]]

    def _safe_div_df(self, conn, portfolio_id: int) -> pd.DataFrame:
        """
        Load dividends and normalize columns to: date, symbol, amount.
        Works with old 'ticker' column too.
        """
        try:
            df = pd.read_sql_query(
                """SELECT date, symbol, amount
                   FROM dividends WHERE portfolio_id=? ORDER BY date""",
                conn,
                params=(portfolio_id,),
            )
            return df
        except Exception:
            df = pd.read_sql_query(
                "SELECT * FROM dividends WHERE portfolio_id=? ORDER BY date",
                conn,
                params=(portfolio_id,),
            )
            if "symbol" not in df.columns and "ticker" in df.columns:
                df["symbol"] = df["ticker"]
            elif "symbol" not in df.columns:
                df["symbol"] = ""
            if "amount" not in df.columns:
                df["amount"] = 0.0
            if "date" not in df.columns:
                df["date"] = ""
            return df[["date", "symbol", "amount"]]

    def _safe_cash_df(self, conn, portfolio_id: int) -> pd.DataFrame:
        """
        Load cash records normalized to: date, amount, note.
        """
        try:
            df = pd.read_sql_query(
                """SELECT date, amount, COALESCE(note,'') AS note
                   FROM cash WHERE portfolio_id=? ORDER BY date""",
                conn,
                params=(portfolio_id,),
            )
            return df
        except Exception:
            df = pd.read_sql_query(
                "SELECT * FROM cash WHERE portfolio_id=? ORDER BY date",
                conn,
                params=(portfolio_id,),
            )
            if "amount" not in df.columns:
                df["amount"] = 0.0
            if "date" not in df.columns:
                df["date"] = ""
            if "note" not in df.columns:
                df["note"] = ""
            return df[["date", "amount", "note"]]

    # --------------------------- UI ----------------------------

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

        names = [name for _, name in portfolios]
        selected_name = st.selectbox("Portfolio", names)
        portfolio_id = [pid for pid, nm in portfolios if nm == selected_name][0]

        with sqlite3.connect(DB_FILE) as conn:
            tx = self._safe_tx_df(conn, portfolio_id)
            dv = self._safe_div_df(conn, portfolio_id)
            cash = self._safe_cash_df(conn, portfolio_id)

        # ---- Top metrics
        c1, c2, c3, c4 = st.columns(4)

        buys = tx[tx["type"].str.upper() == "BUY"] if not tx.empty else pd.DataFrame()
        sells = tx[tx["type"].str.upper() == "SELL"] if not tx.empty else pd.DataFrame()

        buys_val = (buys["quantity"] * buys["price"]).sum() if not buys.empty else 0.0
        sells_val = (sells["quantity"] * sells["price"]).sum() if not sells.empty else 0.0
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

        tx = tx.copy()
        tx["qty_signed"] = tx.apply(
            lambda r: r["quantity"] if str(r["type"]).upper() == "BUY" else -r["quantity"],
            axis=1,
        )
        net_qty = tx.groupby("symbol", dropna=False)["qty_signed"].sum()

        buys_only = tx[tx["type"].str.upper() == "BUY"].copy()
        if buys_only.empty:
            st.info("No BUY transactions to compute holdings.")
            return

        buys_only["notional"] = buys_only["quantity"] * buys_only["price"]
        sum_notional = buys_only.groupby("symbol")["notional"].sum()
        sum_qty = buys_only.groupby("symbol")["quantity"].sum()
        wavg = (sum_notional / sum_qty).replace([pd.NA, pd.NaT], 0).fillna(0)

        df = pd.DataFrame(
            {
                "Symbol": net_qty.index,
                "Net Quantity": net_qty.values,
                "Avg Buy Price": wavg.reindex(net_qty.index).fillna(0).values,
            }
        )

        df = df[df["Net Quantity"] > 0].sort_values("Symbol").reset_index(drop=True)

        if df.empty:
            st.info("No open positions at the moment.")
        else:
            df["Invested (PKR)"] = (df["Net Quantity"] * df["Avg Buy Price"]).round(2)
            st.dataframe(df, use_container_width=True)
