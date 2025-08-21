import streamlit as st
import pandas as pd
import datetime

# Try real data loaders; fall back to safe stubs if unavailable
try:
    from trackerbazaar.data import load_psx_data, excel_date_to_datetime
except Exception:
    def load_psx_data():
        # Safe fallback: no prices available
        return {}
    def excel_date_to_datetime(x):
        if isinstance(x, (int, float)):
            # Excel serial date → datetime (Excel epoch: 1899-12-30)
            return datetime.datetime(1899, 12, 30) + datetime.timedelta(days=float(x))
        return x

def ensure_tracker_defaults(tracker):
    """Ensure required attributes exist to avoid AttributeError on fresh instances."""
    for name, default in [
        ("transactions", []),
        ("holdings", {}),
        ("dividends", {}),
        ("realized_gain", 0.0),
        ("cash", 0.0),
        ("initial_cash", 0.0),
        ("current_prices", {}),
        ("target_allocations", {}),
        ("target_investment", 0.0),
        ("last_div_per_share", {}),
        ("cash_deposits", []),
        ("alerts", []),
        ("filer_status", "Filer"),
        ("broker_fees", {
            'commission_per_share': 0.03,
            'commission_min': 20.0,
            'cdc_fee': 5.0,
            'nccpl_fee_rate': 0.00015,
            'commission_rate': 0.003,
            'sst_low_price': 0.0045,
            'brokerage_rate': 0.0015,
            'sst_rate': 0.15
        }),
    ]:
        if not hasattr(tracker, name):
            setattr(tracker, name, default)

def initialize_tracker(tracker):
    """Initialize the PortfolioTracker with default data and settings."""
    ensure_tracker_defaults(tracker)
    prices = load_psx_data()
    if prices:
        tracker.current_prices = prices
        tracker.target_allocations = {ticker: 0.0 for ticker in prices.keys()}
        st.success("Tracker initialized with current prices.")
    else:
        # keep whatever is there, but ensure it's at least a dict
        tracker.current_prices = getattr(tracker, "current_prices", {}) or {}
        st.warning("No price data available. Initialization skipped.")
    if not getattr(tracker, "cash_deposits", None):
        tracker.cash_deposits = []
        tracker.cash = tracker.cash or 0.0
        tracker.initial_cash = tracker.initial_cash or 0.0

class PortfolioTracker:
    def __init__(self):
        self.transactions = []
        self.holdings = {}
        self.dividends = {}
        self.realized_gain = 0.0
        self.cash = 0.0
        self.initial_cash = 0.0
        self.current_prices = {}            # <-- ensures attribute exists
        self.target_allocations = {}
        self.target_investment = 410000.0
        self.last_div_per_share = {}
        self.cash_deposits = []
        self.alerts = []
        self.filer_status = 'Filer'
        self.broker_fees = {
            'commission_per_share': 0.03,
            'commission_min': 20.0,
            'cdc_fee': 5.0,
            'nccpl_fee_rate': 0.00015,
            'commission_rate': 0.003,
            'sst_low_price': 0.0045,
            'brokerage_rate': 0.0015,
            'sst_rate': 0.15
        }

    # === Example methods (keep your existing implementations below) ===
    def add_transaction(self, txn_date, ticker, trans_type, quantity, price, fee=0.0):
        """Add a transaction to the portfolio (simplified guard clauses)."""
        if isinstance(txn_date, int):
            txn_date = excel_date_to_datetime(txn_date)
        if not isinstance(txn_date, (datetime.datetime, datetime.date)):
            raise ValueError("Invalid date format")
        if trans_type not in ["Buy", "Sell", "Deposit", "Withdraw"]:
            raise ValueError("Invalid transaction type")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Cash movements
        if trans_type in ("Deposit", "Withdraw"):
            amount = float(price)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0 for cash movements")
            if trans_type == "Deposit":
                self.cash += amount
                self.cash_deposits.append({"date": txn_date, "amount": amount})
            else:
                if amount > self.cash:
                    raise ValueError("Insufficient cash to withdraw")
                self.cash -= amount
            self.transactions.append({
                "date": txn_date, "ticker": None, "type": trans_type,
                "quantity": 0, "price": amount, "fee": 0.0
            })
            return

        # Equity trades
        if ticker not in self.current_prices:
            raise ValueError(f"Ticker {ticker} not found in current prices")
        if price <= 0:
            raise ValueError("Price must be greater than 0")

        total_cost = quantity * price + fee
        if trans_type == "Buy":
            if total_cost > self.cash:
                raise ValueError("Insufficient cash for purchase")
            self.cash -= total_cost
            pos = self.holdings.get(ticker, {"qty": 0, "avg_price": 0.0, "invested": 0.0})
            new_qty = pos["qty"] + quantity
            new_invested = pos["invested"] + (quantity * price + fee)
            new_avg = (new_invested / new_qty) if new_qty else 0.0
            self.holdings[ticker] = {"qty": new_qty, "avg_price": new_avg, "invested": new_invested}

        elif trans_type == "Sell":
            pos = self.holdings.get(ticker, {"qty": 0, "avg_price": 0.0, "invested": 0.0})
            if quantity > pos["qty"]:
                raise ValueError("Cannot sell more than current position")
            proceeds = quantity * price - fee
            self.cash += proceeds
            # realize gain against average cost
            realized = (price - pos["avg_price"]) * quantity - fee
            self.realized_gain += realized
            remaining_qty = pos["qty"] - quantity
            if remaining_qty == 0:
                self.holdings.pop(ticker, None)
            else:
                self.holdings[ticker] = {
                    "qty": remaining_qty,
                    "avg_price": pos["avg_price"],
                    "invested": pos["avg_price"] * remaining_qty
                }
        else:
            raise ValueError("Unsupported transaction type")

        self.transactions.append({
            "date": txn_date, "ticker": ticker, "type": trans_type,
            "quantity": quantity, "price": price, "fee": fee
        })

    def get_portfolio(self):
        """Return a DataFrame summarizing holdings (example UI aggregation)."""
        rows = []
        for tkr, pos in (self.holdings or {}).items():
            cur = self.current_prices.get(tkr, 0.0)
            market_value = pos["qty"] * cur
            gain = market_value - pos["invested"]
            roi = (gain / pos["invested"] * 100.0) if pos["invested"] else 0.0
            rows.append({
                "Ticker": tkr,
                "Quantity": pos["qty"],
                "Avg Buy Price": pos["avg_price"],
                "Current Price": cur,
                "Total Invested": pos["invested"],
                "Market Value": market_value,
                "Gain/Loss": gain,
                "ROI %": roi,
            })
        return pd.DataFrame(rows)
