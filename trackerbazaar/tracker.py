import streamlit as st
import pandas as pd
import datetime  # ✅ use full module
from trackerbazaar.data import load_psx_data, excel_date_to_datetime

def initialize_tracker(tracker):
    """Initialize the PortfolioTracker with default data and settings."""
    prices = load_psx_data()
    if prices:
        tracker.current_prices = prices
        tracker.target_allocations = {ticker: 0.0 for ticker in prices.keys()}
        st.success("Tracker initialized with current prices.")
    else:
        st.warning("No price data available. Initialization skipped.")
    if not tracker.cash_deposits:
        tracker.cash_deposits = []
        tracker.cash = 0.0
        tracker.initial_cash = 0.0

class PortfolioTracker:
    def __init__(self):
        self.transactions = []
        self.holdings = {}
        self.dividends = {}
        self.realized_gain = 0.0
        self.cash = 0.0
        self.initial_cash = 0.0
        self.current_prices = {}
        self.target_allocations = {}
        self.target_investment = 410000.0
        self.last_div_per_share = {}
        self.cash_deposits = []
        self.alerts = []
        self.filer_status = 'Filer'
        self.broker_fees = {
            'low_price_fee': 0.03,
            'sst_low_price': 0.0045,
            'brokerage_rate': 0.0015,
            'sst_rate': 0.15
        }

    def add_transaction(self, txn_date, ticker, trans_type, quantity, price, fee=0.0):
        """Add a transaction to the portfolio."""
        if isinstance(txn_date, int):
            txn_date = excel_date_to_datetime(txn_date)
        if not isinstance(txn_date, (datetime.datetime, datetime.date)):
            raise ValueError("Invalid date format")
        if trans_type not in ["Buy", "Sell", "Deposit", "Withdraw"]:
            raise ValueError("Invalid transaction type")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Handle cash transactions
        if trans_type in ["Deposit", "Withdraw"]:
            if ticker is not None:
                raise ValueError("Ticker must be None for Deposit/Withdraw")
            if price != 0.0:
                raise ValueError("Price must be 0 for Deposit/Withdraw")
            if fee != 0.0:
                raise ValueError("Fee must be 0 for Deposit/Withdraw")
            if trans_type == "Withdraw" and quantity > self.cash:
                raise ValueError("Insufficient cash for withdrawal")

            if trans_type == "Deposit":
                self.cash += quantity
                self.initial_cash += quantity
                self.cash_deposits.append({'date': txn_date, 'amount': quantity})
            else:
                self.cash -= quantity

            self.transactions.append({
                'date': txn_date,
                'ticker': None,
                'type': trans_type,
                'quantity': quantity,
                'price': 0.0,
                'fee': 0.0,
                'total': quantity,
                'realized': 0.0
            })

            self.alerts.append({
                'date': datetime.datetime.now(),
                'message': f"{trans_type} of PKR {quantity:.2f} processed"
            })
            return

        # Handle Buy/Sell
        if ticker not in self.current_prices:
            raise ValueError(f"Ticker {ticker} not found in current prices")
        if price <= 0:
            raise ValueError("Price must be greater than 0")
        total_cost = quantity * price + fee

        if trans_type == "Buy":
            if total_cost > self.cash:
                raise ValueError("Insufficient cash for purchase")
            self.cash -= total_cost
            if ticker not in self.holdings:
                self.holdings[ticker] = {'shares': 0.0, 'total_cost': 0.0, 'purchase_date': txn_date}
            self.holdings[ticker]['shares'] += quantity
            self.holdings[ticker]['total_cost'] += total_cost
            self.holdings[ticker]['purchase_date'] = txn_date
        else:
            if ticker not in self.holdings or self.holdings[ticker]['shares'] < quantity:
                raise ValueError("Insufficient shares to sell")
            self.cash += quantity * price - fee
            avg_cost_per_share = self.holdings[ticker]['total_cost'] / self.holdings[ticker]['shares']
            realized_gain = (price - avg_cost_per_share) * quantity - fee
            self.realized_gain += realized_gain
            self.holdings[ticker]['shares'] -= quantity
            self.holdings[ticker]['total_cost'] -= avg_cost_per_share * quantity
            if self.holdings[ticker]['shares'] == 0:
                del self.holdings[ticker]

        self.transactions.append({
            'date': txn_date,
            'ticker': ticker,
            'type': trans_type,
            'quantity': quantity,
            'price': price,
            'fee': fee,
            'total': total_cost if trans_type == "Buy" else quantity * price - fee,
            'realized': realized_gain if trans_type == "Sell" else 0.0
        })

        self.alerts.append({
            'date': datetime.datetime.now(),
            'message': f"{trans_type} {quantity:.2f} shares of {ticker} at PKR {price:.2f}"
        })
