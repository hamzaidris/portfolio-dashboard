import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json

# --- Utility Functions ---
def excel_date_to_datetime(serial):
    """Convert Excel serial date to Python datetime."""
    try:
        return datetime(1900, 1, 1) + timedelta(days=int(serial) - 2)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Excel serial date: {serial}")

# --- Data Fetching Module ---
class DataFetcher:
    @staticmethod
    @st.cache_data(ttl=43200)  # Cache for 12 hours
    def fetch_psx_data():
        """Fetch stock prices and Sharia compliance from PSX Terminal APIs."""
        prices = {}
        fallback_prices = {
            'MLCF': {'price': 83.48, 'sharia': True},
            'GCIL': {'price': 26.70, 'sharia': True},
            'MEBL': {'price': 374.98, 'sharia': True},
            'OGDC': {'price': 272.69, 'sharia': True},
            'GAL': {'price': 529.99, 'sharia': True},
            'GHNI': {'price': 788.00, 'sharia': True},
            'HALEON': {'price': 829.00, 'sharia': True},
            'MARI': {'price': 629.60, 'sharia': True},
            'GLAXO': {'price': 429.99, 'sharia': True},
            'FECTC': {'price': 88.15, 'sharia': True},
            'FFC': {'price': 454.10, 'sharia': False},
            'MUGHAL': {'price': 64.01, 'sharia': False}
        }
        try:
            response = requests.get("https://psxterminal.com/api/market-data", timeout=10)
            response.raise_for_status()
            try:
                response_json = response.json()
                if not isinstance(response_json, dict):
                    st.error(f"Market data API returned unexpected type: {type(response_json)}. Using fallback prices.")
                    return fallback_prices
                market_data = response_json.get("data", [])
                if isinstance(market_data, dict):
                    for ticker, item in market_data.items():
                        price = item.get("price") if isinstance(item, dict) else None
                        if ticker and price is not None:
                            try:
                                prices[ticker] = {"price": float(price), "sharia": False}
                            except (ValueError, TypeError):
                                st.warning(f"Invalid price for {ticker}: {price}")
                                continue
                elif isinstance(market_data, list):
                    for item in market_data:
                        if not isinstance(item, dict):
                            st.warning(f"Skipping invalid market data item: {item}")
                            continue
                        ticker = item.get("symbol")
                        price = item.get("price")
                        if ticker and price is not None:
                            try:
                                prices[ticker] = {"price": float(price), "sharia": False}
                            except (ValueError, TypeError):
                                st.warning(f"Invalid price for {ticker}: {price}")
                                continue
                else:
                    st.error(f"Market data 'data' field is not a list or dict: {type(market_data)}. Using fallback prices.")
                    return fallback_prices
            except json.JSONDecodeError:
                st.error(f"Failed to parse market data API response as JSON: {response.text}. Using fallback prices.")
                return fallback_prices
        except requests.RequestException as e:
            st.error(f"Error fetching market data from PSX Terminal: {e}. Using fallback prices.")
            return fallback_prices

        symbols = ",".join(prices.keys())
        if symbols:
            try:
                response = requests.get(f"https://psxterminal.com/api/yields/{symbols}", timeout=10)
                response.raise_for_status()
                try:
                    response_json = response.json()
                    yields_data = response_json.get("data", [])
                    if isinstance(yields_data, dict):
                        yields_data = [yields_data]
                    if not isinstance(yields_data, list):
                        st.error(f"Yields 'data' field is not a list: {type(yields_data)}. Using fallback prices.")
                        return prices or fallback_prices
                    for item in yields_data:
                        if not isinstance(item, dict):
                            st.warning(f"Skipping invalid yields data item: {item}")
                            continue
                        ticker = item.get("symbol")
                        price = item.get("price")
                        is_non_compliant = item.get("isNonCompliant", True)
                        if ticker and price is not None:
                            try:
                                prices[ticker]["price"] = float(price)
                                prices[ticker]["sharia"] = not is_non_compliant
                            except (ValueError, TypeError):
                                st.warning(f"Invalid price for {ticker}: {price}")
                                continue
                except json.JSONDecodeError:
                    st.error(f"Failed to parse yields API response as JSON: {response.text}. Using fallback prices.")
                    return prices or fallback_prices
            except requests.RequestException as e:
                st.error(f"Error fetching yields data from PSX Terminal: {e}. Using fallback prices.")
                return prices or fallback_prices

        return prices or fallback_prices

# --- Portfolio Tracker Core ---
class PortfolioTracker:
    def __init__(self):
        self.transactions = []
        self.holdings = {}
        self.dividends = {}
        self.realized_gain = 0.0
        self.cash = 0.0
        self.initial_cash = 0.0
        self.current_prices = DataFetcher.fetch_psx_data()
        self.target_allocations = {
            'MLCF': 18.0, 'GCIL': 15.0, 'MEBL': 10.0, 'OGDC': 12.0, 'GAL': 11.0,
            'GHNI': 10.0, 'HALEON': 7.0, 'MARI': 7.0, 'GLAXO': 6.0, 'FECTC': 4.0,
            'FFC': 0.0, 'MUGHAL': 0.0
        }
        self.target_investment = 410000.0
        self.last_div_per_share = {
            'MLCF': 10.0, 'GCIL': 11.0, 'MEBL': 13.0, 'OGDC': 14.0, 'GAL': 15.0,
            'GHNI': 16.0, 'HALEON': 18.0, 'MARI': 19.0, 'GLAXO': 20.0, 'FECTC': 21.0,
            'FFC': 21.0, 'MUGHAL': 17.0
        }
        self.cash_deposits = []

    def add_transaction(self, date, ticker, trans_type, quantity, price, fee=0.0):
        if isinstance(date, int):
            date = excel_date_to_datetime(date)
        trans = {
            'date': date, 'ticker': ticker, 'type': trans_type,
            'quantity': quantity, 'price': price, 'fee': fee
        }
        if trans_type == 'Buy':
            cost = quantity * price + fee
            self.cash -= cost
            if ticker not in self.holdings:
                self.holdings[ticker] = {'shares': 0.0, 'total_cost': 0.0, 'purchase_date': date}
            elif date < self.holdings[ticker]['purchase_date']:
                self.holdings[ticker]['purchase_date'] = date
            self.holdings[ticker]['shares'] += quantity
            self.holdings[ticker]['total_cost'] += cost
            trans['total'] = -cost
            trans['realized'] = 0.0
        elif trans_type == 'Sell':
            if ticker not in self.holdings or self.holdings[ticker]['shares'] < quantity:
                raise ValueError(f"Not enough shares of {ticker} to sell.")
            avg = self.holdings[ticker]['total_cost'] / self.holdings[ticker]['shares']
            gain = quantity * price - quantity * avg
            net = quantity * price - fee
            self.realized_gain += gain - fee
            self.cash += net
            self.holdings[ticker]['total_cost'] -= quantity * avg
            self.holdings[ticker]['shares'] -= quantity
            if self.holdings[ticker]['shares'] <= 0:
                del self.holdings[ticker]
            trans['total'] = net
            trans['realized'] = gain - fee
        elif trans_type == 'Deposit':
            self.cash += quantity
            self.initial_cash += quantity
            self.cash_deposits.append({'date': date, 'amount': quantity})
            trans['total'] = quantity
            trans['realized'] = 0.0
            trans['price'] = 0.0
            trans['fee'] = 0.0
        else:
            raise ValueError("Unsupported transaction type.")
        self.transactions.append(trans)

    def add_dividend(self, ticker, amount):
        if ticker not in self.dividends:
            self.dividends[ticker] = 0.0
        self.dividends[ticker] += amount
        self.cash += amount
        self.transactions.append({
            'date': datetime.now(), 'ticker': ticker, 'type': 'Dividend',
            'quantity': 0, 'price': 0.0, 'fee': 0.0, 'total': amount, 'realized': 0.0
        })

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
        elif trans['type'] == 'Sell':
            self.cash -= trans['total']
            self.realized_gain -= trans['realized']
            if trans['ticker'] not in self.holdings:
                self.holdings[trans['ticker']] = {'shares': 0.0, 'total_cost': 0.0, 'purchase_date': trans['date']}
            gain = trans['realized'] + trans['fee']
            avg = trans['price'] - gain / trans['quantity'] if trans['quantity'] > 0 else 0
            self.holdings[trans['ticker']]['shares'] += trans['quantity']
            self.holdings[trans['ticker']]['total_cost'] += trans['quantity'] * avg
        elif trans['type'] == 'Deposit':
            self.cash -= trans['total']
            self.initial_cash -= trans['total']
            self.cash_deposits = [d for d in self.cash_deposits if d['amount'] != trans['total'] or d['date'] != trans['date']]
        elif trans['type'] == 'Dividend':
            self.cash -= trans['total']
            self.dividends[trans['ticker']] -= trans['total']

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
            portfolio.append({
                'Stock': ticker, 'Shares': shares, 'Avg Buy': round(avg_buy, 2),
                'Total Invested': round(h['total_cost'], 2), 'Current Price': round(current_price, 2),
                'Market Value': round(market_value, 2), 'Gain/Loss': round(gain_loss, 2),
                '% Gain': round(per_gain * 100, 2), 'Dividends': round(div, 2),
                'ROI %': round(roi, 2), 'Target Allocation %': target_allocation,
                'Sharia Compliant': sharia, 'Current Allocation %': round(current_allocation, 2),
                'Allocation Delta %': round(current_allocation - target_allocation, 2)
            })
        return pd.DataFrame(portfolio).sort_values(by='Market Value', ascending=False)

    def get_dashboard(self, current_prices=None):
        portfolio_df = self.get_portfolio(current_prices)
        total_portfolio_value = portfolio_df['Market Value'].sum()
        total_unrealized = portfolio_df['Gain/Loss'].sum()
        total_dividends = portfolio_df['Dividends'].sum()
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
        cash_flows = [t for t in self.transactions if t['type'] in ['Deposit', 'Dividend', 'Buy', 'Sell']]
        return pd.DataFrame(cash_flows)

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
            timeline.append({'date': d, 'profit_loss': profit_loss})
        return pd.DataFrame(timeline)

    def get_cash_to_invest(self):
        total_deposits = sum(d['amount'] for d in self.cash_deposits)
        return self.cash + total_deposits

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
                'Stock': ticker, 'Target Allocation %': target,
                'Current Value': round(current_value, 2), 'Target Value': round(target_value, 2),
                'Delta Value': round(delta_value, 2), 'Suggested Shares': round(suggested_shares, 2)
            })
        return pd.DataFrame(plan).sort_values(by='Delta Value', ascending=False)

    def update_target_allocations(self, new_allocations):
        total = sum(new_allocations.values())
        if abs(total - 100.0) > 0.01:
            raise ValueError(f"Target allocations must sum to 100%, got {total}%")
        self.target_allocations = new_allocations
        st.session_state.tracker.target_allocations = new_allocations

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
                fee_per = 0.03
                sst_per = 0.0045
                total_per = P + fee_per + sst_per
                U = int(dist / total_per)
                fee = U * fee_per
                sst = U * sst_per
            else:
                brokerage_rate = 0.0015
                sst_rate = brokerage_rate * 0.15
                total_rate = brokerage_rate + sst_rate
                investable = dist / (1 + total_rate)
                U = int(investable / P)
                fee = U * P * brokerage_rate
                sst = fee * 0.15
            net_invested = U * P + fee + sst
            leftover = dist - net_invested
            dist_list.append({
                'Stock': ticker, 'Distributed': round(dist, 2), 'Price': P, 'Units': U,
                'Fee': round(fee, 2), 'SST': round(sst, 2), 'Net Invested': round(net_invested, 2),
                'Leftover': round(leftover, 2)
            })
        return pd.DataFrame(dist_list)

    def execute_distribution(self, dist_df, date):
        for _, row in dist_df.iterrows():
            if row['Units'] > 0:
                self.add_transaction(date, row['Stock'], 'Buy', row['Units'], row['Price'], row['Fee'] + row['SST'])
        self.cash_deposits = []

# --- UI Components ---
class PortfolioUI:
    @staticmethod
    def initialize_tracker():
        tracker = PortfolioTracker()
        tracker.add_transaction(excel_date_to_datetime(45665), None, 'Deposit', 414375.28, 0)
        transactions = [
            (45665, 'FECTC', 'Buy', 26, 84.14, 0), (45665, 'FFC', 'Buy', 12, 457.75, 8.24),
            # ... (other transactions remain unchanged)
            (45969, 'MLCF', 'Buy', 115, 83.48, 0)
        ]
        for trans in transactions:
            try:
                tracker.add_transaction(*trans)
            except ValueError as e:
                st.error(f"Error adding transaction {trans}: {e}")
        return tracker

    @staticmethod
    def display_dashboard(tracker):
        st.header("Dashboard")
        dashboard = tracker.get_dashboard()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Portfolio Value", f"PKR {dashboard['Total Portfolio Value']:,.2f}")
        col2.metric("Total ROI %", f"{dashboard['Total ROI %']:.2f}%")
        col3.metric("Total Dividends", f"PKR {dashboard['Total Dividends']:,.2f}")
        col4.metric("Cash Balance", f"PKR {tracker.cash:,.2f}")
        col1.metric("Total Invested", f"PKR {dashboard['Total Invested']:,.2f}")
        col2.metric("Total Realized Gain", f"PKR {dashboard['Total Realized Gain']:,.2f}")
        col3.metric("Total Unrealized Gain", f"PKR {dashboard['Total Unrealized Gain']:,.2f}")
        col4.metric("% of Target Invested", f"{dashboard['% of Target Invested']:.2f}%")

        portfolio_df = tracker.get_portfolio()
        if not portfolio_df.empty:
            fig_bar = px.bar(
                portfolio_df, x='Stock', y=['Market Value', 'Gain/Loss'],
                title='Portfolio Value and Gains/Losses by Stock', barmode='group',
                color_discrete_map={'Market Value': '#636EFA', 'Gain/Loss': '#EF553B'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            fig_alloc = px.bar(
                portfolio_df, x='Stock', y=['Current Allocation %', 'Target Allocation %'],
                title='Current vs Target Allocation', barmode='group',
                color_discrete_map={'Current Allocation %': '#636EFA', 'Target Allocation %': '#00CC96'}
            )
            st.plotly_chart(fig_alloc, use_container_width=True)

            invested_df = tracker.get_invested_timeline()
            if not invested_df.empty:
                fig_invested = px.line(invested_df, x='date', y='invested', title='Amount Invested Over Time')
                st.plotly_chart(fig_invested, use_container_width=True)

            pl_df = tracker.get_profit_loss_timeline()
            if not pl_df.empty:
                fig_pl = px.line(pl_df, x='date', y='profit_loss', title='Profit/Loss Over Time (Approximate)')
                st.plotly_chart(fig_pl, use_container_width=True)
            else:
                st.info("Historical profit/loss data not available.")

    @staticmethod
    def display_add_transaction(tracker):
        st.header("Add Transaction")
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", value=datetime.now())
                current_prices = DataFetcher.fetch_psx_data()
                ticker_options = sorted(current_prices.keys())
                ticker = st.selectbox("Ticker", ticker_options, index=0 if ticker_options else None, key="ticker_select")
            with col2:
                trans_type = st.selectbox("Type", ["Buy", "Sell", "Deposit"])
                quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
                price = st.number_input(
                    "Price", min_value=0.0, step=0.01,
                    value=current_prices.get(ticker, {'price': 0.0})['price']
                )
                fee = st.number_input("Fee", min_value=0.0, value=0.0, step=0.01)
            submit = st.form_submit_button("Add Transaction")
            if submit:
                try:
                    tracker.add_transaction(date, ticker if trans_type != "Deposit" else None, trans_type, quantity, price, fee)
                    st.success("Transaction added successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

    # Other UI methods (portfolio, distribution, etc.) remain similar but can be added modularly

def main():
    st.set_page_config(page_title="Portfolio Dashboard", layout="wide")
    st.title("📈 Portfolio Dashboard")

    if 'tracker' not in st.session_state:
        st.session_state.tracker = PortfolioUI.initialize_tracker()

    tracker = st.session_state.tracker
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Transaction"])  # Add other pages as needed

    if page == "Dashboard":
        PortfolioUI.display_dashboard(tracker)
    elif page == "Add Transaction":
        PortfolioUI.display_add_transaction(tracker)

if __name__ == '__main__':
    main()
