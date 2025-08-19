import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import pytz
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_psx_data():
    """Load stock data from market-data.json and Sharia compliance from kmi_shares.txt."""
    # Load Sharia-compliant stocks from kmi_shares.txt
    sharia_compliant = set()
    try:
        with open("kmi_shares.txt", "r") as f:
            sharia_compliant = {line.strip() for line in f if line.strip()}
        logger.info(f"Loaded {len(sharia_compliant)} Sharia-compliant stocks from kmi_shares.txt")
    except FileNotFoundError:
        logger.error("kmi_shares.txt not found. Returning empty data.")
        st.warning("kmi_shares.txt not found. Please ensure the file is present.")
        return {}
    except Exception as e:
        logger.error(f"Error reading kmi_shares.txt: {e}. Returning empty data.")
        st.warning(f"Error reading kmi_shares.txt: {e}. Please check the file.")
        return {}

    # Load market data from market-data.json
    try:
        with open("market-data.json", "r") as f:
            market_data = json.load(f)
        if not isinstance(market_data, dict) or not market_data.get("success", False):
            logger.error("Invalid market-data.json format. Returning empty data.")
            st.warning("Invalid market-data.json format. Please check the file.")
            return {}
        
        market_data_content = market_data.get("data", {})
        if not isinstance(market_data_content, dict):
            logger.error(f"Market data 'data' field is not a dict: {type(market_data_content)}. Returning empty data.")
            st.warning("Invalid market-data.json structure. Please check the file.")
            return {}

        prices = {}
        for market, stocks in market_data_content.items():
            if not isinstance(stocks, dict):
                logger.warning(f"Skipping invalid market data for {market}: {stocks}")
                continue
            for ticker, item in stocks.items():
                if not isinstance(item, dict):
                    logger.warning(f"Skipping invalid stock data for {ticker}: {item}")
                    continue
                price = item.get("price")
                if ticker and price is not None:
                    try:
                        # Map ticker to Sharia-compliant name if possible
                        sharia_name = next((name for name in sharia_compliant if ticker in name or name.lower().replace(" ", "") == ticker.lower()), ticker)
                        is_sharia = sharia_name in sharia_compliant
                        prices[ticker] = {
                            "price": float(price),
                            "sharia": is_sharia,
                            "type": "Stock" if market == "REG" else "Bond" if market == "BNB" else item.get("type", "Stock"),
                            "change": item.get("change", 0.0),
                            "changePercent": item.get("changePercent", 0.0) * 100,
                            "volume": item.get("volume", 0),
                            "trades": item.get("trades", 0),
                            "value": item.get("value", 0.0),
                            "high": item.get("high", 0.0),
                            "low": item.get("low", 0.0),
                            "bid": item.get("bid", 0.0),
                            "ask": item.get("ask", 0.0),
                            "bidVol": item.get("bidVol", 0),
                            "askVol": item.get("askVol", 0),
                            "timestamp": datetime.fromtimestamp(item.get("timestamp", 0)).isoformat() if item.get("timestamp") else datetime.now(pytz.UTC).isoformat()
                        }
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid price for {ticker}: {price}")
                        continue

        logger.info(f"Processed {len(prices)} tickers from market-data.json")
        if not prices:
            st.warning("No valid data in market-data.json. Please check the file.")
            return {}
        st.info(f"Loaded {len(prices)} tickers from market-data.json")
        return prices

    except FileNotFoundError:
        logger.error("market-data.json not found. Returning empty data.")
        st.warning("market-data.json not found. Please ensure the file is present.")
        return {}
    except json.JSONDecodeError:
        logger.error("Failed to parse market-data.json. Returning empty data.")
        st.warning("Failed to parse market-data.json. Please check the file.")
        return {}
    except Exception as e:
        logger.error(f"Error processing market-data.json: {e}. Returning empty data.")
        st.warning(f"Error processing market-data.json: {e}. Please check the file.")
        return {}

def excel_date_to_datetime(serial):
    """Convert Excel serial date to Python datetime."""
    try:
        return datetime(1900, 1, 1) + timedelta(days=int(serial) - 2)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Excel serial date: {serial}")

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
        self.target_allocations = new_allocations
        st.session_state.tracker.target_allocations = new_allocations
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

def main():
    st.set_page_config(page_title="TrackerBazaar - Portfolio Dashboard", layout="wide")
    st.title("📈 TrackerBazaar - Portfolio Dashboard")
    st.markdown("A portfolio management platform for tracking and optimizing your investments across stocks, mutual funds, and commodities. Stay ahead with real-time insights and analytics.")

    if 'tracker' not in st.session_state:
        st.session_state.tracker = PortfolioTracker()
        initialize_tracker(st.session_state.tracker)
        st.session_state.update_allocations = False
        st.session_state.update_filer_status = False

    tracker = st.session_state.tracker

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Portfolio", "Distribution", "Investment Plan", "Cash", "Stock Explorer", "Notifications", "Transactions", "Current Prices", "Add Transaction", "Add Dividend", "Broker Fees"])

    st.sidebar.header("Tax Settings")
    filer_status = st.sidebar.selectbox("Filer Status", ["Filer", "Non-Filer"], index=0 if tracker.filer_status == 'Filer' else 1)
    if filer_status != tracker.filer_status:
        tracker.update_filer_status(filer_status)

    if st.session_state.get('update_filer_status', False) or st.session_state.get('update_allocations', False):
        st.session_state.update_filer_status = False
        st.session_state.update_allocations = False
        st.rerun()

    if page == "Dashboard":
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
                portfolio_df,
                x='Stock',
                y=['Market Value', 'Gain/Loss'],
                title='Portfolio Value and Gains/Losses by Asset',
                barmode='group',
                color_discrete_map={'Market Value': '#636EFA', 'Gain/Loss': '#EF553B'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            fig_alloc = px.bar(
                portfolio_df,
                x='Stock',
                y=['Current Allocation %', 'Target Allocation %'],
                title='Current vs Target Allocation',
                barmode='group',
                color_discrete_map={'Current Allocation %': '#636EFA', 'Target Allocation %': '#00CC96'}
            )
            st.plotly_chart(fig_alloc, use_container_width=True)

            invested_df = tracker.get_invested_timeline()
            if not invested_df.empty:
                fig_invested = px.line(
                    invested_df,
                    x='date',
                    y='invested',
                    title='Amount Invested Over Time'
                )
                st.plotly_chart(fig_invested, use_container_width=True)

            pl_df = tracker.get_profit_loss_timeline()
            if not pl_df.empty:
                fig_pl = px.line(
                    pl_df,
                    x='date',
                    y='profit_loss',
                    title='Profit/Loss Over Time (Approximate)'
                )
                st.plotly_chart(fig_pl, use_container_width=True)
            else:
                st.info("Historical profit/loss data not available.")
        else:
            st.info("Your portfolio is empty. Add transactions to get started.")

    elif page == "Portfolio":
        st.header("Portfolio Summary")
        portfolio_df = tracker.get_portfolio()
        if not portfolio_df.empty:
            st.dataframe(
                portfolio_df,
                column_config={
                    "Market Value": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Total Invested": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Gain/Loss": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Dividends": st.column_config.NumberColumn(format="PKR %.2f"),
                    "% Gain": st.column_config.NumberColumn(format="%.2f%"),
                    "ROI %": st.column_config.NumberColumn(format="%.2f%"),
                    "Current Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                    "Target Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                    "Allocation Delta %": st.column_config.NumberColumn(format="%.2f%"),
                    "CGT (Potential)": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Sharia Compliant": st.column_config.TextColumn(
                        "Sharia Compliant",
                        help="✅ = Sharia Compliant, ❌ = Non-Compliant"
                    )
                },
                use_container_width=True
            )
            fig_pie = px.pie(
                portfolio_df,
                values='Total Invested',
                names='Stock',
                title='Portfolio Allocation (Based on Invested Amount)',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No holdings in portfolio. Add transactions via 'Add Transaction'.")

    elif page == "Distribution":
        st.header("Distribution Analysis")
        portfolio_df = tracker.get_portfolio()
        dist_df = pd.DataFrame(columns=['Stock', 'Current Allocation %', 'Target Allocation %', 'Allocation Delta %', 'Sharia Compliant'])
        if not portfolio_df.empty:
            dist_df = portfolio_df[['Stock', 'Current Allocation %', 'Target Allocation %', 'Allocation Delta %', 'Sharia Compliant']]
        st.dataframe(
            dist_df,
            column_config={
                "Current Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                "Target Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                "Allocation Delta %": st.column_config.NumberColumn(format="%.2f%"),
                "Sharia Compliant": st.column_config.TextColumn(
                    "Sharia Compliant",
                    help="✅ = Sharia Compliant, ❌ = Non-Compliant"
                )
            },
            use_container_width=True
        )
        if not dist_df.empty:
            fig_dist = px.bar(
                dist_df,
                x='Stock',
                y=['Current Allocation %', 'Target Allocation %'],
                title='Current vs Target Allocation',
                barmode='group',
                color_discrete_map={'Current Allocation %': '#636EFA', 'Target Allocation %': '#00CC96'}
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.info("No holdings to analyze. Add transactions to view distribution.")

        st.subheader("Edit Target Allocations")
        with st.form("edit_allocations_form"):
            st.write("Select stocks and enter target allocation percentages (must sum to 100%)")
            selected_tickers = st.multiselect("Select Stocks", options=sorted(tracker.current_prices.keys()), default=list(tracker.target_allocations.keys()))
            new_allocations = {}
            for ticker in tracker.current_prices.keys():
                new_allocations[ticker] = 0.0
            if selected_tickers:
                cols = st.columns(min(len(selected_tickers), 5))
                for i, ticker in enumerate(selected_tickers):
                    with cols[i % 5]:
                        new_allocations[ticker] = st.number_input(
                            f"{ticker} (%)", min_value=0.0, max_value=100.0, value=tracker.target_allocations.get(ticker, 0.0), step=0.1
                        )
            submit = st.form_submit_button("Update Allocations")
            if submit:
                try:
                    tracker.update_target_allocations(new_allocations)
                    st.success("Target allocations updated successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

        st.subheader("Edit or Remove Distribution")
        if selected_tickers:
            edit_ticker = st.selectbox("Select Stock to Edit or Remove", options=selected_tickers)
            if edit_ticker:
                new_percentage = st.number_input(
                    f"New Percentage for {edit_ticker} (%)", min_value=0.0, max_value=100.0, value=tracker.target_allocations.get(edit_ticker, 0.0), step=0.1
                )
                if st.button("Update Percentage"):
                    tracker.target_allocations[edit_ticker] = new_percentage
                    st.success(f"Percentage for {edit_ticker} updated to {new_percentage}%")
                    st.rerun()

                if st.button("Remove Stock"):
                    tracker.target_allocations[edit_ticker] = 0.0
                    st.success(f"{edit_ticker} removed from distribution.")
                    st.rerun()
        else:
            st.info("No stocks selected for editing or removal.")

    elif page == "Investment Plan":
        st.header("Investment Plan")
        plan_df = tracker.get_investment_plan()
        if not plan_df.empty:
            st.dataframe(
                plan_df,
                column_config={
                    "Current Value": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Target Value": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Delta Value": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Target Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                    "Suggested Shares": st.column_config.NumberColumn(format="%.2f")
                },
                use_container_width=True
            )
            st.write("**Note**: Positive 'Delta Value' suggests buying, negative suggests selling.")
        else:
            st.info("No investment plan available. Add transactions to generate rebalancing suggestions.")

        st.subheader("Add and Distribute Cash")
        with st.form("distribute_cash_form"):
            date = st.date_input("Date", value=datetime.now())
            cash = st.number_input("Cash to Add and Distribute (PKR)", min_value=0.0, step=100.0)
            sharia_only = st.checkbox("Distribute only to Sharia-compliant stocks", value=False)
            submit_calc = st.form_submit_button("Calculate Distribution")
        if submit_calc:
            if sharia_only:
                sharia_allocations = {
                    ticker: alloc for ticker, alloc in tracker.target_allocations.items()
                    if tracker.current_prices.get(ticker, {'sharia': False})['sharia'] and alloc > 0
                }
                if not sharia_allocations:
                    st.error("No Sharia-compliant stocks with positive allocations.")
                else:
                    total_alloc = sum(sharia_allocations.values())
                    if total_alloc == 0:
                        st.error("Total allocation for Sharia-compliant stocks is 0.")
                    else:
                        normalized_allocations = {ticker: alloc / total_alloc * 100 for ticker, alloc in sharia_allocations.items()}
                        temp_tracker = PortfolioTracker()
                        temp_tracker.target_allocations = normalized_allocations
                        temp_tracker.current_prices = tracker.current_prices
                        dist_df = temp_tracker.calculate_distribution(cash)
                        st.session_state.dist_df = dist_df
                        st.dataframe(
                            dist_df,
                            column_config={
                                "Distributed": st.column_config.NumberColumn(format="PKR %.2f"),
                                "Price": st.column_config.NumberColumn(format="PKR %.2f"),
                                "Fee": st.column_config.NumberColumn(format="PKR %.2f"),
                                "SST": st.column_config.NumberColumn(format="PKR %.2f"),
                                "Net Invested": st.column_config.NumberColumn(format="PKR %.2f"),
                                "Leftover": st.column_config.NumberColumn(format="PKR %.2f")
                            },
                            use_container_width=True
                        )
            else:
                dist_df = tracker.calculate_distribution(cash)
                st.session_state.dist_df = dist_df
                st.dataframe(
                    dist_df,
                    column_config={
                        "Distributed": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Price": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Fee": st.column_config.NumberColumn(format="PKR %.2f"),
                        "SST": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Net Invested": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Leftover": st.column_config.NumberColumn(format="PKR %.2f")
                    },
                    use_container_width=True
                )

    elif page == "Cash":
        st.header("Cash Summary")
        tabs = st.tabs(["Cash Flow", "Add Cash", "Cash Available", "Withdraw Cash"])

        with tabs[0]:
            cash_df = tracker.get_cash_summary()
            if not cash_df.empty:
                cash_df['date'] = pd.to_datetime(cash_df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(
                    cash_df,
                    column_config={
                        "quantity": st.column_config.NumberColumn(format="PKR %.2f")
                    },
                    use_container_width=True
                )
            else:
                st.info("No cash transactions recorded. Add a deposit to start.")
            st.metric("Current Cash Balance", f"PKR {tracker.cash:,.2f}")
            dashboard = tracker.get_dashboard()
            st.metric("Total Invested Amount", f"PKR {dashboard['Total Invested']:,.2f}")

        with tabs[1]:
            with st.form("add_cash_form"):
                date = st.date_input("Deposit Date", value=datetime.now())
                amount = st.number_input("Deposit Amount (PKR)", min_value=0.0, step=100.0)
                submit = st.form_submit_button("Add Cash")
                if submit:
                    try:
                        tracker.add_transaction(date, None, 'Deposit', amount, 0.0)
                        st.success("Cash deposited successfully!")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Error: {e}")

        with tabs[2]:
            cash_to_invest = tracker.get_cash_to_invest()
            st.metric("Cash Available", f"PKR {cash_to_invest:,.2f}")
            deposits_df = pd.DataFrame(tracker.cash_deposits)
            if not deposits_df.empty:
                deposits_df['date'] = pd.to_datetime(deposits_df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(
                    deposits_df,
                    column_config={
                        "amount": st.column_config.NumberColumn(format="PKR %.2f")
                    },
                    use_container_width=True
                )
            else:
                st.info("No new cash deposits recorded.")
            st.write(f"Previous Cash Available: PKR {tracker.cash:,.2f}")

        with tabs[3]:
            st.subheader("Withdraw Cash")
            with st.form("withdraw_cash_form"):
                date = st.date_input("Withdrawal Date", value=datetime.now())
                amount = st.number_input("Withdrawal Amount (PKR)", min_value=0.0, step=100.0)
                submit = st.form_submit_button("Withdraw Cash")
                if submit:
                    try:
                        tracker.add_transaction(date, None, 'Withdraw', amount, 0.0)
                        st.success("Cash withdrawn successfully!")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Error: {e}")

    elif page == "Stock Explorer":
        st.header("Stock Explorer")
        st.write("Search and explore investment opportunities across stocks, mutual funds, and commodities.")
        prices_df = pd.DataFrame([
            {
                'Ticker': k,
                'Price': v['price'],
                'Sharia Compliant': '✅' if v['sharia'] else '❌',
                'Type': v.get('type', 'Stock'),
                'Change': v.get('change', 0.0),
                'Change %': v.get('changePercent', 0.0),
                'Volume': v.get('volume', 0),
                'Trades': v.get('trades', 0),
                'Value': v.get('value', 0.0),
                'High': v.get('high', 0.0),
                'Low': v.get('low', 0.0),
                'Bid': v.get('bid', 0.0),
                'Ask': v.get('ask', 0.0),
                'Bid Volume': v.get('bidVol', 0),
                'Ask Volume': v.get('askVol', 0),
                'Timestamp': v.get('timestamp', datetime.now())
            }
            for k, v in tracker.current_prices.items()
        ])
        if not prices_df.empty:
            prices_df['Timestamp'] = pd.to_datetime(prices_df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            search_term = st.text_input("Search by Ticker or Name")
            asset_type = st.selectbox("Asset Type", ["All", "Stock", "Mutual Fund", "Commodity", "Bond"])
            sharia_filter = st.checkbox("Show only Sharia-compliant assets", value=False)
            filtered_df = prices_df
            if search_term:
                filtered_df = filtered_df[filtered_df['Ticker'].str.contains(search_term, case=False, na=False)]
            if asset_type != "All":
                filtered_df = filtered_df[filtered_df['Type'] == asset_type]
            if sharia_filter:
                filtered_df = filtered_df[filtered_df['Sharia Compliant'] == '✅']
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df,
                    column_config={
                        "Price": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Change": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Change %": st.column_config.NumberColumn(format="%.2f%"),
                        "Value": st.column_config.NumberColumn(format="PKR %.2f"),
                        "High": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Low": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Bid": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Ask": st.column_config.NumberColumn(format="PKR %.2f"),
                        "Sharia Compliant": st.column_config.TextColumn(
                            "Sharia Compliant",
                            help="✅ = Sharia Compliant, ❌ = Non-Compliant"
                        )
                    },
                    use_container_width=True
                )
            else:
                st.info("No assets match the search criteria.")
        else:
            st.info("No stock data available. Ensure market-data.json and kmi_shares.txt are present.")

    elif page == "Notifications":
        st.header("Notifications")
        st.write("Real-time alerts for price movements, trades, and portfolio updates.")
        alerts_df = tracker.get_alerts()
        if not alerts_df.empty:
            alerts_df['date'] = pd.to_datetime(alerts_df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(alerts_df, use_container_width=True)
        else:
            st.info("No notifications available. Add transactions to generate alerts.")

    elif page == "Transactions":
        st.header("Transaction History")
        if tracker.transactions:
            trans_df = pd.DataFrame(tracker.transactions)
            if not trans_df.empty:
                trans_df['date'] = pd.to_datetime(trans_df['date']).dt.strftime('%Y-%m-%d')
                trans_df['Select'] = False
                edited_df = st.data_editor(
                    trans_df,
                    column_config={
                        "Select": st.column_config.CheckboxColumn(),
                        "total": st.column_config.NumberColumn(format="PKR %.2f"),
                        "realized": st.column_config.NumberColumn(format="PKR %.2f"),
                        "price": st.column_config.NumberColumn(format="PKR %.2f"),
                        "fee": st.column_config.NumberColumn(format="PKR %.2f")
                    },
                    use_container_width=True,
                    hide_index=False
                )
                selected = edited_df[edited_df['Select']].index.tolist()
                if st.button("Delete Selected Transactions"):
                    try:
                        for index in sorted(selected, reverse=True):
                            tracker.delete_transaction(index)
                        st.success("Selected transactions deleted successfully!")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Error: {e}")
        else:
            st.info("No transactions recorded. Add transactions via 'Add Transaction'.")

    elif page == "Current Prices":
        st.header("Current Prices")
        prices_list = [{
            'Ticker': k,
            'Price': v['price'],
            'Sharia Compliant': '✅' if v['sharia'] else '❌',
            'Type': v.get('type', 'Stock'),
            'Change': v.get('change', 0.0),
            'Change %': v.get('changePercent', 0.0),
            'Volume': v.get('volume', 0),
            'Trades': v.get('trades', 0),
            'Value': v.get('value', 0.0),
            'High': v.get('high', 0.0),
            'Low': v.get('low', 0.0),
            'Bid': v.get('bid', 0.0),
            'Ask': v.get('ask', 0.0),
            'Bid Volume': v.get('bidVol', 0),
            'Ask Volume': v.get('askVol', 0),
            'Timestamp': v.get('timestamp', datetime.now())
        } for k, v in tracker.current_prices.items()]
        prices_df = pd.DataFrame(prices_list)
        if not prices_df.empty:
            prices_df['Timestamp'] = pd.to_datetime(prices_df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            edited_df = st.data_editor(
                prices_df,
                column_config={
                    "Price": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Change": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Change %": st.column_config.NumberColumn(format="%.2f%"),
                    "Value": st.column_config.NumberColumn(format="PKR %.2f"),
                    "High": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Low": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Bid": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Ask": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Sharia Compliant": st.column_config.TextColumn(
                        "Sharia Compliant",
                        help="✅ = Sharia Compliant, ❌ = Non-Compliant"
                    )
                },
                num_rows="dynamic",
                use_container_width=True,
                key="prices_editor"
            )
            if st.button("Update Prices"):
                updated_prices = {}
                for _, row in edited_df.iterrows():
                    ticker = row['Ticker']
                    updated_prices[ticker] = {
                        'price': row['Price'],
                        'sharia': row['Sharia Compliant'] == '✅',
                        'type': row['Type'],
                        'change': row['Change'],
                        'changePercent': row['Change %'],
                        'volume': row['Volume'],
                        'trades': row['Trades'],
                        'value': row['Value'],
                        'high': row['High'],
                        'low': row['Low'],
                        'bid': row['Bid'],
                        'ask': row['Ask'],
                        'bidVol': row['Bid Volume'],
                        'askVol': row['Ask Volume'],
                        'timestamp': pd.to_datetime(row['Timestamp'])
                    }
                tracker.current_prices = updated_prices
                st.success("Prices updated successfully!")
        else:
            st.info("No stock data available. Ensure market-data.json and kmi_shares.txt are present.")

    elif page == "Add Transaction":
        st.header("Add Transaction")
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", value=datetime.now())
                ticker_options = sorted(tracker.current_prices.keys())
                ticker = st.selectbox("Ticker", ticker_options, index=0 if ticker_options else None)
                trans_type = st.selectbox("Type", ["Buy", "Sell", "Deposit", "Withdraw"])
            with col2:
                quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
                price = st.number_input("Price", min_value=0.0, step=0.01, value=tracker.current_prices.get(ticker, {'price': 0.0})['price'] if ticker else 0.0)
                fee = st.number_input("Fee", min_value=0.0, value=0.0, step=0.01)
            submit = st.form_submit_button("Add Transaction")
            if submit:
                try:
                    tracker.add_transaction(date, ticker if trans_type in ["Buy", "Sell"] else None, trans_type, quantity, price, fee)
                    st.success("Transaction added successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

    elif page == "Add Dividend":
        st.header("Add Dividend")
        with st.form("dividend_form"):
            ticker_options = sorted(tracker.current_prices.keys())
            ticker = st.selectbox("Ticker", ticker_options, index=0 if ticker_options else None)
            amount = st.number_input("Dividend Amount", min_value=0.0, step=0.01)
            submit = st.form_submit_button("Add Dividend")
            if submit:
                try:
                    tracker.add_dividend(ticker, amount)
                    st.success("Dividend added successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

    elif page == "Broker Fees":
        st.header("Broker Fees")
        st.write("Define your broker fees for distribution calculations.")
        with st.form("broker_fees_form"):
            low_price_fee = st.number_input("Low Price Fee (P <= 20)", min_value=0.0, value=tracker.broker_fees.get('low_price_fee', 0.03), step=0.01)
            sst_low_price = st.number_input("SST for Low Price (P <= 20)", min_value=0.0, value=tracker.broker_fees.get('sst_low_price', 0.0045), step=0.0001)
            brokerage_rate = st.number_input("Brokerage Rate (P > 20)", min_value=0.0, value=tracker.broker_fees.get('brokerage_rate', 0.0015), step=0.0001)
            sst_rate = st.number_input("SST Rate for Brokerage", min_value=0.0, value=tracker.broker_fees.get('sst_rate', 0.15), step=0.01)
            submit = st.form_submit_button("Update Broker Fees")
            if submit:
                tracker.broker_fees = {
                    'low_price_fee': low_price_fee,
                    'sst_low_price': sst_low_price,
                    'brokerage_rate': brokerage_rate,
                    'sst_rate': sst_rate
                }
                st.success("Broker fees updated successfully!")

if __name__ == '__main__':
    main()
