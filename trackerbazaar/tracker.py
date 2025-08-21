import streamlit as st
import pandas as pd
from datetime import datetime, date
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
        """Add a transaction to the portfolio."""
        import datetime
        if isinstance(date, int):
            date = excel_date_to_datetime(date)
        if not isinstance(date, (datetime.datetime, datetime.date)):
            raise ValueError("Invalid date format")
        if trans_type not in ["Buy", "Sell", "Deposit", "Withdraw"]:
            raise ValueError("Invalid transaction type")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Handle cash transactions (Deposit/Withdraw)
        if trans_type in ["Deposit", "Withdraw"]:
            if ticker is not None:
                raise ValueError("Ticker must be None for Deposit/Withdraw")
            if price != 0.0:
                raise ValueError("Price must be 0 for Deposit/Withdraw")
            if fee != 0.0:
                raise ValueError("Fee must be 0 for Deposit/Withdraw")
            if trans_type == "Withdraw" and quantity > self.cash:
                raise ValueError("Insufficient cash for withdrawal")

            # Update cash balance
            if trans_type == "Deposit":
                self.cash += quantity
                self.initial_cash += quantity
                self.cash_deposits.append({'date': date, 'amount': quantity})
            else:  # Withdraw
                self.cash -= quantity

            # Log transaction
            self.transactions.append({
                'date': date,
                'ticker': None,
                'type': trans_type,
                'quantity': quantity,
                'price': 0.0,
                'fee': 0.0,
                'total': quantity,
                'realized': 0.0
            })

            # Generate alert
            self.alerts.append({
                'date': datetime.now(),
                'message': f"{trans_type} of PKR {quantity:.2f} processed"
            })
            return

        # Handle Buy/Sell transactions
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
                self.holdings[ticker] = {'shares': 0.0, 'total_cost': 0.0, 'purchase_date': date}
            self.holdings[ticker]['shares'] += quantity
            self.holdings[ticker]['total_cost'] += total_cost
            self.holdings[ticker]['purchase_date'] = date  # Update to latest purchase date
        else:  # Sell
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

        # Log transaction
        self.transactions.append({
            'date': date,
            'ticker': ticker,
            'type': trans_type,
            'quantity': quantity,
            'price': price,
            'fee': fee,
            'total': total_cost if trans_type == "Buy" else quantity * price - fee,
            'realized': realized_gain if trans_type == "Sell" else 0.0
        })

        # Generate alert
        self.alerts.append({
            'date': datetime.now(),
            'message': f"{trans_type} {quantity:.2f} shares of {ticker} at PKR {price:.2f}"
        })

    def get_invested_timeline(self):
        """Return a DataFrame with the cumulative invested capital over time."""
        timeline = []
        cumulative_invested = 0.0

        # Combine transactions and cash deposits for timeline
        events = []
        for trans in self.transactions:
            events.append({
                'date': trans['date'],
                'type': trans['type'],
                'amount': trans['total'] if trans['type'] in ['Buy', 'Deposit'] else -trans['total']
            })
        for deposit in self.cash_deposits:
            events.append({
                'date': deposit['date'],
                'type': 'Deposit',
                'amount': deposit['amount']
            })

        # Sort events by date
        events.sort(key=lambda x: x['date'])

        # Calculate cumulative invested amount
        for event in events:
            if event['type'] in ['Buy', 'Deposit']:
                cumulative_invested += event['amount']
            elif event['type'] == 'Sell':
                cumulative_invested += event['amount']  # Negative amount reduces invested capital
            # Skip Withdraw transactions as they affect cash but not invested capital
            timeline.append({
                'date': event['date'],
                'invested': max(cumulative_invested, 0.0)  # Ensure non-negative
            })

        # Convert to DataFrame and ensure unique dates
        df = pd.DataFrame(timeline)
        if not df.empty:
            df = df.groupby('date', as_index=False).last()  # Keep last entry for each date
            df['date'] = pd.to_datetime(df['date'])  # Ensure date is datetime
            df = df.sort_values('date')  # Sort by date
        return df if not df.empty else pd.DataFrame(columns=['date', 'invested'])

    def get_profit_loss_timeline(self):
        """Return a DataFrame with the unrealized profit/loss over time."""
        timeline = []
        
        # Get unique dates from transactions
        dates = sorted(set(trans['date'] for trans in self.transactions if trans['type'] in ['Buy', 'Sell']))
        
        # Calculate profit/loss for each date based on holdings
        for date in dates:
            total_market_value = 0.0
            total_invested = 0.0
            for ticker, data in self.holdings.items():
                # Only consider holdings purchased on or before the current date
                if data['purchase_date'] <= date:
                    current_price = self.current_prices.get(ticker, {}).get('price', 0.0)
                    market_value = data['shares'] * current_price
                    total_market_value += market_value
                    total_invested += data['total_cost']
            profit_loss = total_market_value - total_invested
            timeline.append({
                'date': date,
                'profit_loss': profit_loss
            })

        # Convert to DataFrame and ensure unique dates
        df = pd.DataFrame(timeline)
        if not df.empty:
            df = df.groupby('date', as_index=False).last()  # Keep last entry for each date
            df['date'] = pd.to_datetime(df['date'])  # Ensure date is datetime
            df = df.sort_values('date')  # Sort by date
        return df if not df.empty else pd.DataFrame(columns=['date', 'profit_loss'])

    def get_cash_summary(self):
        """Return a DataFrame summarizing cash transactions."""
        cash_summary = []
        for trans in self.transactions:
            if trans['type'] in ['Deposit', 'Withdraw']:
                cash_summary.append({
                    'date': trans['date'],
                    'type': trans['type'],
                    'quantity': trans['quantity'],
                    'price': trans['price'],
                    'fee': trans['fee']
                })
        return pd.DataFrame(cash_summary) if cash_summary else pd.DataFrame()

    def get_alerts(self):
        """Return a DataFrame of alerts."""
        return pd.DataFrame(self.alerts) if self.alerts else pd.DataFrame(columns=['date', 'message'])

    def update_filer_status(self, status):
        self.filer_status = status

    def add_dividend(self, ticker, amount):
        if ticker not in self.current_prices:
            raise ValueError(f"Ticker {ticker} not found")
        if amount <= 0:
            raise ValueError("Dividend amount must be greater than 0")
        if ticker not in self.dividends:
            self.dividends[ticker] = 0.0
        self.dividends[ticker] += amount
        self.alerts.append({
            'date': datetime.now(),
            'message': f"Dividend of PKR {amount:.2f} added for {ticker}"
        })

    def update_target_allocations(self, allocations):
        total = sum(allocations.values())
        if abs(total - 100.0) > 0.01 and total != 0:
            raise ValueError("Target allocations must sum to 100% or 0%")
        self.target_allocations = allocations

    def calculate_distribution(self, cash):
        distribution = []
        leftover = cash
        for i, (ticker, alloc) in enumerate(self.target_allocations.items()):
            if alloc <= 0:
                continue
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

    def get_portfolio(self):
        """Return a DataFrame summarizing portfolio holdings."""
        portfolio = []
        for ticker, data in self.holdings.items():
            current_price = self.current_prices.get(ticker, {}).get('price', 0.0)
            market_value = data['shares'] * current_price
            total_invested = data['total_cost']
            gain_loss = market_value - total_invested
            portfolio.append({
                'Stock': ticker,
                'Quantity': data['shares'],
                'Market Value': market_value,
                'Total Invested': total_invested,
                'Gain/Loss': gain_loss,
                'Dividends': self.dividends.get(ticker, 0.0),
                '% Gain': (gain_loss / total_invested * 100) if total_invested > 0 else 0.0,
                'ROI %': ((market_value + self.dividends.get(ticker, 0.0) - total_invested) / total_invested * 100) if total_invested > 0 else 0.0,
                'Current Allocation %': (market_value / self.get_total_portfolio_value() * 100) if self.get_total_portfolio_value() > 0 else 0.0,
                'Target Allocation %': self.target_allocations.get(ticker, 0.0),
                'Allocation Delta %': self.target_allocations.get(ticker, 0.0) - (market_value / self.get_total_portfolio_value() * 100) if self.get_total_portfolio_value() > 0 else 0.0,
                'CGT (Potential)': gain_loss * 0.15 if self.filer_status == 'Filer' else gain_loss * 0.3
            })
        return pd.DataFrame(portfolio) if portfolio else pd.DataFrame()

    def get_total_portfolio_value(self):
        """Calculate total portfolio value including cash."""
        total = self.cash
        for ticker, data in self.holdings.items():
            total += data['shares'] * self.current_prices.get(ticker, {}).get('price', 0.0)
        return total

    def get_dashboard(self):
        """Return dashboard metrics."""
        portfolio = self.get_portfolio()
        total_invested = sum(self.holdings.get(ticker, {}).get('total_cost', 0.0) for ticker in self.holdings)
        total_market_value = sum(self.holdings.get(ticker, {}).get('shares', 0.0) * self.current_prices.get(ticker, {}).get('price', 0.0) for ticker in self.holdings)
        total_dividends = sum(self.dividends.values())
        total_unrealized_gain = total_market_value - total_invested
        total_roi = ((total_market_value + total_dividends - total_invested) / total_invested * 100) if total_invested > 0 else 0.0
        return {
            'Total Portfolio Value': total_market_value + self.cash,
            'Total Invested': total_invested,
            'Total Realized Gain': self.realized_gain,
            'Total Unrealized Gain': total_unrealized_gain,
            'Total Dividends': total_dividends,
            'Total ROI %': total_roi,
            'Cash Balance': self.cash,
            '% of Target Invested': (total_invested / self.target_investment * 100) if self.target_investment > 0 else 0.0
        }
