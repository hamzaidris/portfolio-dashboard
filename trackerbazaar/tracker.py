import streamlit as st
import pandas as pd
from datetime import datetime
from trackerbazaar.data import load_psx_data, excel_date_to_datetime

def initialize_tracker(tracker):
    """Initialize the PortfolioTracker with default data and settings."""
    # Load current prices and update tracker
    prices = load_psx_data()
    if prices:
        tracker.current_prices = prices
        # Set default target allocations (e.g., 0% for all tickers)
        tracker.target_allocations = {ticker: 0.0 for ticker in prices.keys()}
        st.success("Tracker initialized with current prices.")
    else:
        st.warning("No price data available. Initialization skipped.")
    # Ensure initial cash and holdings are set to zero by default
    if not tracker.cash_deposits:
        tracker.cash_deposits = []
        tracker.cash = 0.0
        tracker.initial_cash = 0.0

class PortfolioTracker:
    def __init__(self):
        self.transactions = []
        self.holdings = {}  # ticker: {'shares': float, 'total_cost': float, 'purchase_date': date}
        self.dividends = {}  # ticker: total_dividends since purchase
        self.realized_gain = 0.0
        self.cash = 0.0
        self.initial_cash = 0.0
        self.current_prices = {}  # Initialized empty, to be set by initialize_tracker
        self.target_allocations = {}
        self.target_investment = 410000.0
        self.last_div_per_share = {}
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
            self.realized_gain -= trans['realized']
            if trans['ticker'] not in self.holdings:
                self.holdings[trans['ticker']] = {'shares': 0.0, 'total_cost': 0.0, 'purchase_date': trans['date']}
            gain = trans['realized'] + trans['fee']
            avg = trans['price'] - gain / trans['quantity'] if trans['quantity'] > 0 else 0
            self.holdings[trans['ticker']]['shares'] += trans['quantity']
            self.holdings[trans['ticker']]['total_cost'] += trans['quantity'] * avg
            self.add_alert(f"Deleted Sell transaction for {trans['quantity']} shares of {trans['ticker']} on {trans['date'].strftime('%Y-%m-%d')}")
        elif trans['type'] == 'Deposit':
            self.cash -= trans['total']
            self.initial_cash -= trans['total']
            self.cash_deposits = [d for d in self.cash_deposits if d['amount'] != trans['total'] or d['date'] != trans['date']]
            self.add_alert(f"Deleted Deposit of PKR {trans['total']} on {trans['date'].strftime('%Y-%m-%d')}")
        elif trans['type'] == 'Withdraw':
            self.cash += trans['total']
            self.add_alert(f"Deleted Withdrawal of PKR {-trans['total']} on {trans['date'].strftime('%Y-%m-%d')}")
        elif trans['type'] == 'Dividend':
            self.cash -= trans['total']
            self.dividends[trans['ticker']] -= trans['total']
            self.add_alert(f"Deleted Dividend of PKR {trans['total']} for {trans['ticker']} on {trans['date'].strftime('%Y-%m-%d')}")

    def get_portfolio(self, current_prices=None):
        portfolio = []
        current_prices = current_prices or self.current_prices
        total_value = self.cash
        for ticker, holding in self.holdings.items():
            if ticker in current_prices:
                market_value = holding['shares'] * current_prices[ticker]['price']
                total_invested = holding['total_cost']
                gain_loss = market_value - total_invested
                dividends = self.dividends.get(ticker, 0.0)
                pct_gain = (gain_loss / total_invested * 100) if total_invested > 0 else 0.0
                roi = ((market_value + dividends) / total_invested * 100) if total_invested > 0 else 0.0
                current_alloc = (market_value / (total_value + market_value) * 100) if total_value + market_value > 0 else 0.0
                target_alloc = self.target_allocations.get(ticker, 0.0)
                alloc_delta = current_alloc - target_alloc
                cgt_potential = gain_loss * (0.125 if self.filer_status == 'Filer' else 0.15) if gain_loss > 0 else 0.0
                portfolio.append({
                    'Stock': ticker,
                    'Shares': holding['shares'],
                    'Market Value': market_value,
                    'Total Invested': total_invested,
                    'Gain/Loss': gain_loss,
                    'Dividends': dividends,
                    '% Gain': pct_gain,
                    'ROI %': roi,
                    'Current Allocation %': current_alloc,
                    'Target Allocation %': target_alloc,
                    'Allocation Delta %': alloc_delta,
                    'CGT (Potential)': cgt_potential,
                    'Sharia Compliant': '✅' if current_prices[ticker]['sharia'] else '❌'
                })
                total_value += market_value
        return pd.DataFrame(portfolio) if portfolio else pd.DataFrame()

    def get_dashboard(self):
        """Return a dictionary of key portfolio metrics."""
        portfolio_df = self.get_portfolio()
        total_portfolio_value = self.cash
        total_invested = 0.0
        total_unrealized_gain = 0.0
        total_dividends = sum(self.dividends.values(), 0.0)

        for _, row in portfolio_df.iterrows():
            total_portfolio_value += row['Market Value']
            total_invested += row['Total Invested']
            total_unrealized_gain += row['Gain/Loss']

        total_roi = ((total_portfolio_value + total_dividends) / (total_invested or 1) * 100) if total_invested > 0 else 0.0
        percent_of_target = (total_invested / self.target_investment * 100) if self.target_investment > 0 else 0.0

        return {
            'Total Portfolio Value': total_portfolio_value,
            'Total ROI %': total_roi,
            'Total Dividends': total_dividends,
            'Total Invested': total_invested,
            'Total Realized Gain': self.realized_gain,
            'Total Unrealized Gain': total_unrealized_gain,
            '% of Target Invested': percent_of_target,
            'Cash Balance': self.cash
        }

    def get_invested_timeline(self):
        """Return a DataFrame of invested amount over time."""
        invested_history = []
        for trans in sorted(self.transactions, key=lambda x: x['date']):
            if trans['type'] in ['Buy', 'Deposit']:
                invested = -trans['total'] if trans['type'] == 'Buy' else trans['total']
                invested_history.append({'date': trans['date'], 'invested': invested})
        return pd.DataFrame(invested_history) if invested_history else pd.DataFrame()

    def get_profit_loss_timeline(self):
        """Return a DataFrame of approximate profit/loss over time."""
        pl_history = []
        cumulative_pl = 0.0
        for trans in sorted(self.transactions, key=lambda x: x['date']):
            if trans['type'] == 'Sell':
                cumulative_pl += trans['realized']
                pl_history.append({'date': trans['date'], 'profit_loss': cumulative_pl})
        return pd.DataFrame(pl_history) if pl_history else pd.DataFrame()

    def update_filer_status(self, status):
        """Update the tax filer status."""
        if status not in ['Filer', 'Non-Filer']:
            raise ValueError("Invalid filer status. Use 'Filer' or 'Non-Filer'.")
        self.filer_status = status
        st.session_state.update_filer_status = True

    def update_target_allocations(self, allocations):
        """Update target allocations, ensuring they sum to 100%."""
        total_alloc = sum(alloc for alloc in allocations.values() if alloc > 0)
        if total_alloc > 100.0 or total_alloc < 99.9:  # Allow slight float precision
            raise ValueError("Target allocations must sum to 100%.")
        self.target_allocations = {ticker: alloc for ticker, alloc in allocations.items()}
        st.session_state.update_allocations = True

    def get_cash_to_invest(self):
        """Return available cash for investment."""
        return self.cash

    def calculate_distribution(self, cash):
        """Calculate how many stocks can be bought based on current prices and target allocations."""
        if not self.target_allocations or sum(self.target_allocations.values()) == 0 or not cash:
            return pd.DataFrame()
        total_alloc = sum(alloc for alloc in self.target_allocations.values() if alloc > 0)
        if total_alloc == 0:
            return pd.DataFrame()
        distribution = []
        leftover = cash
        for i, (ticker, alloc) in enumerate(self.target_allocations.items()):
            if alloc > 0 and ticker in self.current_prices:
                price = self.current_prices[ticker]['price']
                target_amount = (alloc / 100) * cash
                quantity = target_amount // price
                if quantity > 0:
                    fee = self._calculate_fee(price, quantity)
                    sst = self._calculate_sst(price, quantity, fee)
                    net_invested = quantity * price + fee + sst
                    distributed = min(net_invested, target_amount)
                    leftover -= distributed
                    distribution.append({
                        'Stock': ticker,
                        'Quantity': quantity,
                        'Price': price,
                        'Fee': fee,
                        'SST': sst,
                        'Net Invested': net_invested,
                        'Leftover': leftover if i == len(self.target_allocations) - 1 else 0.0
                    })
        return pd.DataFrame(distribution)

    def _calculate_fee(self, price, quantity):
        """Calculate brokerage fee based on price and quantity."""
        if price <= 20:
            return quantity * self.broker_fees['low_price_fee']
        return quantity * price * self.broker_fees['brokerage_rate']

    def _calculate_sst(self, price, quantity, fee):
        """Calculate SST based on price and fee."""
        if price <= 20:
            return quantity * self.broker_fees['sst_low_price']
        return fee * self.broker_fees['sst_rate']

    def get_cash_summary(self):
        """Return a DataFrame summarizing cash transactions."""
        cash_summary = []
        for trans in self.transactions:
            if trans['type'] in ['Deposit', 'Withdraw']:
                cash_summary.append({
                    'date': trans['date'],
                    'type': trans['type'],
                    'quantity': trans['total'],
                    'price': trans['price'],
                    'fee': trans['fee']
                })
        return pd.DataFrame(cash_summary) if cash_summary else pd.DataFrame()
