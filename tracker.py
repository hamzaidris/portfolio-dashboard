import streamlit as st
import pandas as pd
from datetime import datetime
from .data import load_psx_data, excel_date_to_datetime

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
        total_invested = sum(h['total_cost'] for h in self.holdings.values() if h['shares'] > 0)
        total_portfolio_value = 0.0
        for ticker, h in self.holdings.items():
            shares = h['shares']
            if shares <= 0:
                continue
            avg_buy = h['total_cost'] / shares
            current_price = (current_prices.get(ticker) if current_prices else None) or \
                            self.current_prices.get(ticker, {'price': 0.0})['price']
            market_value = shares * current_price
            total_portfolio_value += market_value
            gain_loss = market_value - h['total_cost']
            per_gain = gain_loss / h['total_cost'] if h['total_cost'] > 0 else 0.0
            div = self.last_div_per_share.get(ticker, 0) * shares if h['purchase_date'] <= datetime.now() else 0.0
            roi = (market_value + div) / h['total_cost'] * 100 if h['total_cost'] > 0 else 0.0
            target_allocation = self.target_allocations.get(ticker, 0.0)
            sharia = self.current_prices.get(ticker, {'sharia': False})['sharia']
            current_allocation = (h['total_cost'] / total_invested * 100) if total_invested > 0 else 0.0
            cgt = (market_value - h['total_cost']) * (0.125 if self.filer_status == 'Filer' else 0.15) if market_value > h['total_cost'] else 0.0
            portfolio.append({
                'Stock': ticker,
                'Shares': shares,
                'Avg Buy': round(avg_buy, 2),
                'Total Invested': round(h['total_cost'], 2),
                'Current Price': round(current_price, 2),
                'Market Value': round(market_value, 2),
                'Gain/Loss': round(gain_loss, 2),
                '% Gain': round(per_gain * 100, 2),
                'Dividends': round(div, 2),
                'ROI %': round(roi, 2),
                'Target Allocation %': target_allocation,
                'Sharia Compliant': sharia,
                'Current Allocation %': round(current_allocation, 2),
                'Allocation Delta %': round(current_allocation - target_allocation, 2),
                'CGT (Potential)': round(cgt, 2)
            })
            if abs(per_gain) > 0.1:
                self.add_alert(f"{ticker} has {'gained' if per_gain > 0 else 'lost'} {abs(per_gain*100):.2f}%")
        portfolio_df = pd.DataFrame(portfolio)
        return portfolio_df.sort_values(by='Market Value', ascending=False) if not portfolio_df.empty else pd.DataFrame()

    def get_dashboard(self, current_prices=None):
        portfolio_df = self.get_portfolio(current_prices)
        total_portfolio_value = portfolio_df['Market Value'].sum() if not portfolio_df.empty else 0.0
        total_unrealized = portfolio_df['Gain/Loss'].sum() if not portfolio_df.empty else 0.0
        total_dividends = portfolio_df['Dividends'].sum() if not portfolio_df.empty else 0.0
        total_invested = self.initial_cash - self.cash
        total_roi = (total_portfolio_value + total_dividends) / total_invested * 100 if total_invested > 0 else 0.0
        return {
            'Total Realized Gain': round(self.realized_gain, 2),
            'Total Portfolio Value': round(total_portfolio_value, 2),
            'Total Unrealized Gain': round(total_unrealized, 2),
            'Total Dividends': round(total_dividends, 2),
            'Total Invested': round(total_invested, 2),
            'Target Investment': self.target_investment,
            '% of Target Invested': round(total_invested / self.target_investment * 100, 2) if self.target_investment > 0 else 0.0,
            'Total ROI %': round(total_roi, 2)
        }

    def get_cash_summary(self):
        cash_flows = [
            {'date': t['date'], 'type': t['type'], 'quantity': t['total']}
            for t in self.transactions if t['type'] in ['Deposit', 'Withdraw', 'Dividend', 'Buy', 'Sell']
        ]
        return pd.DataFrame(cash_flows) if cash_flows else pd.DataFrame()

    def get_invested_timeline(self):
        if not self.transactions:
            return pd.DataFrame()
        df = pd.DataFrame(self.transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['invested_change'] = 0.0
        df.loc[df['type'] == 'Buy', 'invested_change'] = -df['total']
        df.loc[df['type'] == 'Sell', 'invested_change'] = df['total']
        df = df.groupby('date')['invested_change'].sum().cumsum().reset_index()
        df['invested'] = df['invested_change']
        return df

    def get_profit_loss_timeline(self):
        if not self.transactions:
            return pd.DataFrame()
        df = pd.DataFrame(self.transactions)
        df['date'] = pd.to_datetime(df['date'])
        dates = pd.date_range(start=df['date'].min(), end=datetime.today(), freq='D')
        timeline = []
        for d in dates:
            past_trans = df[df['date'] <= d]
            invested = 0.0
            market_value = 0.0
            for ticker, h in self.holdings.items():
                if h['shares'] > 0 and h['purchase_date'] <= d:
                    market_value += h['shares'] * self.current_prices.get(ticker, {'price': 0.0})['price']
            for _, row in past_trans.iterrows():
                if row['type'] == 'Buy':
                    invested += -row['total']
                elif row['type'] == 'Sell':
                    invested -= row['total']
            profit_loss = market_value - invested
            timeline.append({
                'date': d,
                'profit_loss': profit_loss
            })
        return pd.DataFrame(timeline)

    def get_cash_to_invest(self):
        cash_to_invest = sum(d['amount'] for d in self.cash_deposits)
        return self.cash + cash_to_invest

    def get_investment_plan(self):
        portfolio_df = self.get_portfolio()
        if portfolio_df.empty:
            return pd.DataFrame()
        total_value = portfolio_df['Market Value'].sum() + self.cash
        plan = []
        for ticker, target in self.target_allocations.items():
            current_value = portfolio_df[portfolio_df['Stock'] == ticker]['Market Value'].sum()
            target_value = total_value * (target / 100)
            delta_value = target_value - current_value
            current_price = self.current_prices.get(ticker, {'price': 0.0})['price']
            suggested_shares = delta_value / current_price if current_price > 0 else 0
            plan.append({
                'Stock': ticker,
                'Target Allocation %': target,
                'Current Value': round(current_value, 2),
                'Target Value': round(target_value, 2),
                'Delta Value': round(delta_value, 2),
                'Suggested Shares': round(suggested_shares, 2)
            })
        return pd.DataFrame(plan).sort_values(by='Delta Value', ascending=False) if plan else pd.DataFrame()

    def update_target_allocations(self, new_allocations):
        total = sum(new_allocations.values())
        if abs(total - 100.0) > 0.01:
            raise ValueError(f"Target allocations must sum to 100%, got {total}%")
        for ticker in self.current_prices.keys():
            self.target_allocations[ticker] = new_allocations.get(ticker, 0.0)
        st.session_state.tracker.target_allocations = self.target_allocations
        self.add_alert("Target allocations updated")
        st.session_state.update_allocations = True

    def update_filer_status(self, status):
        if status != self.filer_status:
            self.filer_status = status
            self.add_alert(f"Filer status updated to {status}")
            st.session_state.update_filer_status = True

    def calculate_distribution(self, cash):
        dist_list = []
        for ticker, target in self.target_allocations.items():
            if target == 0:
                continue
            dist = cash * (target / 100)
            P = self.current_prices.get(ticker, {'price': 0.0})['price']
            if P == 0.0:
                continue
            if P <= 20:
                fee_per = self.broker_fees['low_price_fee']
                sst_per = self.broker_fees['sst_low_price']
                total_per = P + fee_per + sst_per
                U = int(dist / total_per)
                fee = U * fee_per
                sst = U * sst_per
            else:
                brokerage_rate = self.broker_fees['brokerage_rate']
                sst_rate = self.broker_fees['sst_rate']
                total_rate = brokerage_rate + (brokerage_rate * sst_rate)
                investable = dist / (1 + total_rate)
                U = int(investable / P)
                fee = U * P * brokerage_rate
                sst = fee * sst_rate
            net_invested = U * P + fee + sst
            leftover = dist - net_invested
            dist_list.append({
                'Stock': ticker,
                'Distributed': round(dist, 2),
                'Price': P,
                'Units': U,
                'Fee': round(fee, 2),
                'SST': round(sst, 2),
                'Net Invested': round(net_invested, 2),
                'Leftover': round(leftover, 2)
            })
        return pd.DataFrame(dist_list) if dist_list else pd.DataFrame()

    def execute_distribution(self, dist_df, date):
        for index, row in dist_df.iterrows():
            if row['Units'] > 0:
                self.add_transaction(date, row['Stock'], 'Buy', row['Units'], row['Price'], row['Fee'] + row['SST'])
        self.cash_deposits = []

def initialize_tracker(tracker):
    """Initialize tracker without default transactions."""
    pass
