import streamlit as st
import pandas as pd
from datetime import datetime
from trackerbazaar.data import load_psx_data, excel_date_to_datetime

class PortfolioTracker:
    def __init__(self):
        self.transactions = []
        self.holdings = {}  # ticker: {'shares': float, 'total_cost': float, 'purchase_date': date}
        self.dividends = {}  # ticker: total_dividends since purchase
        self.realized_gain = 0.0
        self.cash = 0.0
        self.initial_cash = 0.0
        self.current_prices = load_psx_data()
        self.target_allocations = {ticker: 0.0 for ticker in self.current_prices.keys()}
        self.target_investment = 410000.0
        self.last_div_per_share = {ticker: 0.0 for ticker in self.current_prices.keys()}
        self.cash_deposits = []
        self.alerts = []  # Store notifications
        self.filer_status = 'Filer'  # Default tax status
        self.broker_fees = {
            'low_price_fee': 0.03,  # Fee per unit for P <= 20
            'sst_low_price': 0.0045,  # SST for P <= 20
            'brokerage_rate': 0.0015,  # Brokerage rate for P > 20
            'sst_rate': 0.15  # SST rate for brokerage
        }

    def add_transaction(self, date, ticker, trans_type, quantity, price, fee=0.0):
        if isinstance(date, int):
            date = excel_date_to_datetime(date)
        if not isinstance(date, datetime):
            date = pd.to_datetime(date)
        trans = {
            'date': date,
            'ticker': ticker,
            'type': trans_type,
            'quantity': quantity,
            'price': price,
            'fee': fee
        }
        if trans_type == 'Buy':
            cost = quantity * price + fee
            if cost > self.cash:
                raise ValueError(f"Insufficient cash balance (PKR {self.cash:.2f}) for purchase of PKR {cost:.2f}.")
            self.cash -= cost
            if ticker not in self.holdings:
                self.holdings[ticker] = {'shares': 0.0, 'total_cost': 0.0, 'purchase_date': date}
            elif date < self.holdings[ticker]['purchase_date']:
                self.holdings[ticker]['purchase_date'] = date
            self.holdings[ticker]['shares'] += quantity
            self.holdings[ticker]['total_cost'] += cost
            trans['total'] = -cost
            trans['realized'] = 0.0
            self.add_alert(f"Bought {quantity} shares of {ticker} at PKR {price} on {date.strftime('%Y-%m-%d')}")
        elif trans_type == 'Sell':
            if ticker not in self.holdings or self.holdings[ticker]['shares'] < quantity:
                raise ValueError(f"Not enough shares of {ticker} to sell.")
            avg = self.holdings[ticker]['total_cost'] / self.holdings[ticker]['shares']
            gain = quantity * price - quantity * avg
            net = quantity * price - fee
            cgt = gain * (0.125 if self.filer_status == 'Filer' else 0.15)
            self.realized_gain += gain - fee - cgt
            self.cash += net - cgt
            self.holdings[ticker]['total_cost'] -= quantity * avg
            self.holdings[ticker]['shares'] -= quantity
            if self.holdings[ticker]['shares'] <= 0:
                del self.holdings[ticker]
            trans['total'] = net - cgt
            trans['realized'] = gain - fee - cgt
            self.add_alert(f"Sold {quantity} shares of {ticker} at PKR {price} on {date.strftime('%Y-%m-%d')}, CGT: PKR {cgt:.2f}")
        elif trans_type == 'Deposit':
            self.cash += quantity
            self.initial_cash += quantity
            self.cash_deposits.append({'date': date, 'amount': quantity})
            trans['total'] = quantity
            trans['realized'] = 0.0
            trans['price'] = 0.0
            trans['fee'] = 0.0
            self.add_alert(f"Deposited PKR {quantity} on {date.strftime('%Y-%m-%d')}")
        elif trans_type == 'Withdraw':
            if quantity > self.cash:
                raise ValueError(f"Insufficient cash balance (PKR {self.cash:.2f}) for withdrawal of PKR {quantity:.2f}.")
            self.cash -= quantity
            trans['total'] = -quantity
            trans['realized'] = 0.0
            trans['price'] = 0.0
            trans['fee'] = 0.0
            self.add_alert(f"Withdrew PKR {quantity} on {date.strftime('%Y-%m-%d')}")
        else:
            raise ValueError("Unsupported transaction type.")
        self.transactions.append(trans)

    def add_dividend(self, ticker, amount):
        if ticker not in self.dividends:
            self.dividends[ticker] = 0.0
        self.dividends[ticker] += amount
        self.cash += amount
        self.transactions.append({
            'date': datetime.now(),
            'ticker': ticker,
            'type': 'Dividend',
            'quantity': 0,
            'price': 0.0,
            'fee': 0.0,
            'total': amount,
            'realized': 0.0
        })
        self.add_alert(f"Received dividend of PKR {amount} for {ticker} on {datetime.now().strftime('%Y-%m-%d')}")

    def add_alert(self, message):
        """Add a notification to the alerts list."""
        self.alerts.append({'date': datetime.now(), 'message': message})

    def get_alerts(self):
        """Return recent alerts."""
        return pd.DataFrame(self.alerts[-10:]) if self.alerts else pd.DataFrame()

    def delete_transaction(self, index):
        if index < 0 or index >= len(self.transactions):
            raise ValueError("Invalid transaction index.")
        trans = self.transactions.pop(index)
        if trans['type'] == 'Buy':
            self.cash += -trans['total']
            self.holdings[trans['ticker']]['shares'] -= trans['quantity']
            self.holdings[trans['ticker']]['total_cost'] += trans['total']
            if self.holdings[trans['ticker']]['shares'] <= 0:
                del self.holdings[trans['ticker']]
            self.add_alert(f"Deleted Buy transaction for {trans['quantity']} shares of {trans['ticker']} on {trans['date'].strftime('%Y-%m-%d')}")
        elif trans['type'] == 'Sell':
            self.cash -= trans['total']
            self.realized_gain
