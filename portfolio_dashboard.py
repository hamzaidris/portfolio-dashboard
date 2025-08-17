import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def excel_date_to_datetime(serial):
    """Convert Excel serial date to Python datetime."""
    try:
        return datetime(1900, 1, 1) + timedelta(days=int(serial) - 2)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Excel serial date: {serial}")

@st.cache_data(ttl=43200)  # Cache for 12 hours (43200 seconds)
def fetch_psx_data():
    """Fetch stock prices and Sharia compliance from PSX."""
    prices = {}
    # Fetch prices from market-summary
    url = "https://www.psx.com.pk/market-summary/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='tbldata14')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    ticker = cols[0].text.strip()
                    current_str = cols[4].text.strip().replace(',', '')
                    try:
                        current = float(current_str)
                    except ValueError:
                        continue
                    prices[ticker] = {'price': current, 'sharia': False}
    except requests.RequestException as e:
        st.error(f"Error fetching prices from PSX: {e}")
        return prices

    # Fetch Sharia compliant tickers from KMIALLSHR
    sharia_url = "https://dps.psx.com.pk/indices/KMIALLSHR"
    try:
        sh_response = requests.get(sharia_url, timeout=10)
        sh_response.raise_for_status()
        sh_soup = BeautifulSoup(sh_response.text, 'html.parser')
        sh_table = sh_soup.find('table', class_='tbldata14')
        if sh_table:
            sh_rows = sh_table.find_all('tr')[1:]
            for row in sh_rows:
                cols = row.find_all('td')
                if len(cols) >= 1:
                    ticker = cols[0].text.strip()
                    if ticker in prices:
                        prices[ticker]['sharia'] = True
    except requests.RequestException as e:
        st.error(f"Error fetching Sharia data from PSX: {e}")
    return prices

class PortfolioTracker:
    def __init__(self):
        self.transactions = []
        self.holdings = {}  # ticker: {'shares': float, 'total_cost': float}
        self.dividends = {}  # ticker: total_dividends
        self.realized_gain = 0.0
        self.cash = 0.0
        self.initial_cash = 0.0
        self.current_prices = fetch_psx_data()
        # Target allocations from shariah-re-distribuation sheet
        self.target_allocations = {
            'MLCF': 18.0,
            'GCIL': 15.0,
            'MEBL': 10.0,
            'OGDC': 12.0,
            'GAL': 11.0,
            'GHNI': 10.0,
            'HALEON': 7.0,
            'MARI': 7.0,
            'GLAXO': 6.0,
            'FECTC': 4.0,
            'FFC': 0.0,
            'MUGHAL': 0.0
        }
        self.target_investment = 410000.0  # From InvestmentPlan sheet

    def add_transaction(self, date, ticker, trans_type, quantity, price, fee=0.0):
        """Add a buy, sell, or deposit transaction."""
        if isinstance(date, int):
            date = excel_date_to_datetime(date)
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
            self.cash -= cost
            if ticker not in self.holdings:
                self.holdings[ticker] = {'shares': 0.0, 'total_cost': 0.0}
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
            trans['total'] = quantity
            trans['realized'] = 0.0
            trans['price'] = 0.0
            trans['fee'] = 0.0
        else:
            raise ValueError("Unsupported transaction type.")
        self.transactions.append(trans)

    def add_dividend(self, ticker, amount):
        """Add a dividend payment for a ticker."""
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

    def delete_transaction(self, index):
        """Delete a transaction and recalculate holdings."""
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
                self.holdings[trans['ticker']] = {'shares': 0.0, 'total_cost': 0.0}
            gain = trans['realized'] + trans['fee']
            avg = trans['price'] - gain / trans['quantity'] if trans['quantity'] > 0 else 0
            self.holdings[trans['ticker']]['shares'] += trans['quantity']
            self.holdings[trans['ticker']]['total_cost'] += trans['quantity'] * avg
        elif trans['type'] == 'Deposit':
            self.cash -= trans['total']
            self.initial_cash -= trans['total']
        elif trans['type'] == 'Dividend':
            self.cash -= trans['total']
            self.dividends[trans['ticker']] -= trans['total']

    def get_portfolio(self, current_prices=None):
        """Generate portfolio summary with current prices."""
        portfolio = []
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
            div = self.dividends.get(ticker, 0.0)
            roi = (market_value + div) / h['total_cost'] * 100 if h['total_cost'] > 0 else 0.0
            target_allocation = self.target_allocations.get(ticker, 0.0)
            sharia = self.current_prices.get(ticker, {'sharia': False})['sharia']
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
                'Sharia Compliant': sharia
            })
        portfolio_df = pd.DataFrame(portfolio)
        if total_portfolio_value > 0:
            portfolio_df['Current Allocation %'] = (portfolio_df['Market Value'] / total_portfolio_value * 100).round(2)
            portfolio_df['Allocation Delta %'] = portfolio_df['Current Allocation %'] - portfolio_df['Target Allocation %']
        return portfolio_df.sort_values(by='Market Value', ascending=False)

    def get_dashboard(self, current_prices=None):
        """Generate dashboard summary metrics."""
        portfolio_df = self.get_portfolio(current_prices)
        total_portfolio_value = portfolio_df['Market Value'].sum()
        total_unrealized = portfolio_df['Gain/Loss'].sum()
        total_dividends = sum(self.dividends.values())
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
        """Generate cash flow summary from transactions."""
        cash_flows = [t for t in self.transactions if t['type'] in ['Deposit', 'Dividend', 'Buy', 'Sell']]
        return pd.DataFrame(cash_flows)

    def get_investment_plan(self):
        """Generate investment plan with rebalancing suggestions."""
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
        return pd.DataFrame(plan).sort_values(by='Delta Value', ascending=False)

    def update_target_allocations(self, new_allocations):
        """Update target allocations and validate sum to 100%."""
        total = sum(new_allocations.values())
        if abs(total - 100.0) > 0.01:
            raise ValueError(f"Target allocations must sum to 100%, got {total}%")
        self.target_allocations.update(new_allocations)

    def calculate_distribution(self, cash):
        """Calculate distribution of cash to stocks based on target allocations, with fees."""
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
                'Stock': ticker,
                'Distributed': round(dist, 2),
                'Price': P,
                'Units': U,
                'Fee': round(fee, 2),
                'SST': round(sst, 2),
                'Net Invested': round(net_invested, 2),
                'Leftover': round(leftover, 2)
            })
        return pd.DataFrame(dist_list)

    def execute_distribution(self, dist_df, date):
        """Execute the distribution by adding buy transactions."""
        for index, row in dist_df.iterrows():
            if row['Units'] > 0:
                self.add_transaction(date, row['Stock'], 'Buy', row['Units'], row['Price'], row['Fee'] + row['SST'])

def initialize_tracker(tracker):
    """Initialize tracker with transactions and dividends from Excel."""
    # Initial deposit from Transactions sheet
    tracker.add_transaction(excel_date_to_datetime(45665), None, 'Deposit', 414375.28, 0)
    # Transactions from Transactions sheet
    transactions = [
        (45665, 'FECTC', 'Buy', 26, 84.14, 0),
        (45665, 'FFC', 'Buy', 12, 457.75, 8.24),
        (45665, 'GAL', 'Buy', 8, 510.47, 6.13),
        (45665, 'GCIL', 'Buy', 280, 25.68, 0),
        (45665, 'GHNI', 'Buy', 4, 805, 4.83),
        (45665, 'GLAXO', 'Buy', 6, 426, 3.83),
        (45665, 'HALEON', 'Buy', 3, 827.99, 3.73),
        (45665, 'MARI', 'Buy', 4, 622.27, 0),
        (45665, 'MLCF', 'Buy', 107, 81.82, 0),
        (45665, 'MUGHAL', 'Buy', 150, 64, 14.4),
        (45665, 'MEBL', 'Buy', 15, 362.76, 0),
        (45665, 'OGDC', 'Buy', 23, 234.77, 0),
        (45755, 'FECTC', 'Buy', 164, 85.14, 0),
        (45755, 'FFC', 'Buy', 76, 456.9, 52.09),
        (45755, 'GAL', 'Buy', 53, 518.99, 41.26),
        (45755, 'GCIL', 'Buy', 1766, 25.79, 0),
        (45755, 'GHNI', 'Buy', 26, 801, 31.24),
        (45755, 'GLAXO', 'Buy', 41, 426, 26.2),
        (45755, 'HALEON', 'Buy', 20, 837.85, 25.14),
        (45755, 'MARI', 'Buy', 27, 632.02, 0),
        (45755, 'MLCF', 'Buy', 667, 83.94, 0),
        (45755, 'MUGHAL', 'Buy', 159, 64.02, 15.24),
        (45755, 'OGDC', 'Buy', 134, 260.7, 0),
        (45755, 'MEBL', 'Buy', 96, 363.58, 0),
        (45785, 'FFC', 'Buy', 14, 469.9, 9.87),
        (45785, 'HALEON', 'Buy', 7, 836, 8.78),
        (45785, 'OGDC', 'Buy', 25, 258.7, 0),
        (45816, 'FFC', 'Buy', 18, 460.9, 12.45),
        (45816, 'MEBL', 'Buy', 23, 369.16, 0),
        (45816, 'MUGHAL', 'Sell', 309, 64.01, 29.66),
        (45877, 'FFC', 'Sell', 10, 454.1, 6.82),
        (45877, 'FFC', 'Sell', 19, 454.1, 12.94),
        (45877, 'FFC', 'Sell', 30, 454.1, 20.44),
        (45877, 'FFC', 'Sell', 2, 454.1, 1.36),
        (45877, 'FFC', 'Sell', 59, 454.1, 40.19),
        (45969, 'FECTC', 'Buy', 32, 88.15, 0),
        (45969, 'GAL', 'Buy', 12, 529.99, 9.54),
        (45969, 'GCIL', 'Buy', 300, 26.7, 0),
        (45969, 'GHNI', 'Buy', 7, 788, 8.27),
        (45969, 'GLAXO', 'Buy', 6, 429.99, 3.87),
        (45969, 'HALEON', 'Buy', 5, 829, 6.22),
        (45969, 'MEBL', 'Buy', 15, 374.98, 0),
        (45969, 'OGDC', 'Buy', 21, 272.69, 0),
        (45969, 'MARI', 'Buy', 9, 629.6, 0),
        (45969, 'MLCF', 'Buy', 115, 83.48, 0)
    ]
    for trans in transactions:
        try:
            tracker.add_transaction(*trans)
        except ValueError as e:
            st.error(f"Error adding transaction {trans}: {e}")

    # Dividends from Portfolio sheet
    div_data = {
        'MLCF': 8890,
        'GCIL': 25806,
        'MEBL': 1937,
        'OGDC': 2842,
        'GAL': 1095,
        'GHNI': 592,
        'HALEON': 630,
        'MARI': 760,
        'GLAXO': 1060,
        'FECTC': 4662
    }
    for ticker, amount in div_data.items():
        tracker.add_dividend(ticker, amount)

def main():
    st.set_page_config(page_title="Portfolio Dashboard", layout="wide")
    st.title("📈 Portfolio Dashboard")

    # Initialize session state for tracker
    if 'tracker' not in st.session_state:
        st.session_state.tracker = PortfolioTracker()
        initialize_tracker(st.session_state.tracker)

    tracker = st.session_state.tracker

    # Sidebar for navigation
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Portfolio", "Distribution", "Investment Plan", "Cash", "Transactions", "Current Prices", "Add Transaction", "Add Dividend"])

    if page == "Dashboard":
        st.header("Dashboard")
        dashboard = tracker.get_dashboard()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Portfolio Value", f"PKR {dashboard['Total Portfolio Value']:,.2f}")
        col2.metric("Total ROI %", f"{dashboard['Total ROI %']:.2f}%")
        col3.metric("Total Dividends", f"PKR {dashboard['Total Dividends']:,.2f}")
        col4.metric("Cash Balance", f"PKR {dashboard['Cash Balance']:,.2f}")
        col1.metric("Total Invested", f"PKR {dashboard['Total Invested']:,.2f}")
        col2.metric("Total Realized Gain", f"PKR {dashboard['Total Realized Gain']:,.2f}")
        col3.metric("Total Unrealized Gain", f"PKR {dashboard['Total Unrealized Gain']:,.2f}")
        col4.metric("% of Target Invested", f"{dashboard['% of Target Invested']:.2f}%")
        
        # Portfolio Value Bar Chart
        portfolio_df = tracker.get_portfolio()
        if not portfolio_df.empty:
            fig_bar = px.bar(
                portfolio_df,
                x='Stock',
                y=['Market Value', 'Gain/Loss'],
                title='Portfolio Value and Gains/Losses by Stock',
                barmode='group',
                color_discrete_map={'Market Value': '#636EFA', 'Gain/Loss': '#EF553B'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

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
                    "Sharia Compliant": st.column_config.CheckboxColumn()
                },
                use_container_width=True
            )
            # Allocation Pie Chart
            fig_pie = px.pie(
                portfolio_df,
                values='Market Value',
                names='Stock',
                title='Portfolio Allocation',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No holdings in portfolio.")

    elif page == "Distribution":
        st.header("Distribution Analysis")
        portfolio_df = tracker.get_portfolio()
        if not portfolio_df.empty:
            dist_df = portfolio_df[['Stock', 'Current Allocation %', 'Target Allocation %', 'Allocation Delta %', 'Sharia Compliant']]
            st.dataframe(
                dist_df,
                column_config={
                    "Current Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                    "Target Allocation %": st.column_config.NumberColumn(format="%.2f%"),
                    "Allocation Delta %": st.column_config.NumberColumn(format="%.2f%"),
                    "Sharia Compliant": st.column_config.CheckboxColumn()
                },
                use_container_width=True
            )
            # Bar Chart for Allocation Comparison
            fig_dist = px.bar(
                dist_df,
                x='Stock',
                y=['Current Allocation %', 'Target Allocation %'],
                title='Current vs Target Allocation',
                barmode='group',
                color_discrete_map={'Current Allocation %': '#636EFA', 'Target Allocation %': '#00CC96'}
            )
            st.plotly_chart(fig_dist, use_container_width=True)

            # Edit Target Allocations
            st.subheader("Edit Target Allocations")
            with st.form("edit_allocations_form"):
                st.write("Enter new target allocation percentages (must sum to 100%)")
                new_allocations = {}
                cols = st.columns(5)
                all_tickers = sorted(tracker.current_prices.keys())
                for i, ticker in enumerate(all_tickers):
                    with cols[i % 5]:
                        default = tracker.target_allocations.get(ticker, 0.0)
                        new_allocations[ticker] = st.number_input(
                            f"{ticker} (%)", min_value=0.0, max_value=100.0, value=default, step=0.1
                        )
                submit = st.form_submit_button("Update Allocations")
                if submit:
                    try:
                        tracker.update_target_allocations(new_allocations)
                        st.success("Target allocations updated successfully!")
                    except ValueError as e:
                        st.error(f"Error: {e}")

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

        # Distribute Cash
        st.subheader("Add and Distribute Cash")
        with st.form("distribute_cash_form"):
            date = st.date_input("Date", value=datetime.now())
            cash = st.number_input("Cash to Add and Distribute (PKR)", min_value=0.0, step=100.0)
            sharia_only = st.checkbox("Distribute only to Sharia-compliant stocks", value=False)
            submit_calc = st.form_submit_button("Calculate Distribution")
        if submit_calc:
            if sharia_only:
                # Filter target allocations to Sharia-compliant stocks only
                sharia_allocations = {
                    ticker: alloc for ticker, alloc in tracker.target_allocations.items()
                    if tracker.current_prices.get(ticker, {'sharia': False})['sharia'] and alloc > 0
                }
                if not sharia_allocations:
                    st.error("No Sharia-compliant stocks with positive allocations.")
                else:
                    # Normalize allocations to sum to 100%
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
                        if st.button("Confirm and Execute Distribution"):
                            tracker.add_transaction(date, None, 'Deposit', cash, 0.0)
                            tracker.execute_distribution(dist_df, date)
                            st.success("Cash added and distributed successfully!")
                            st.experimental_rerun()
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
                if st.button("Confirm and Execute Distribution"):
                    tracker.add_transaction(date, None, 'Deposit', cash, 0.0)
                    tracker.execute_distribution(dist_df, date)
                    st.success("Cash added and distributed successfully!")
                    st.experimental_rerun()

    elif page == "Cash":
        st.header("Cash Summary")
        cash_df = tracker.get_cash_summary()
        if not cash_df.empty:
            cash_df['date'] = cash_df['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(
                cash_df,
                column_config={
                    "total": st.column_config.NumberColumn(format="PKR %.2f"),
                    "realized": st.column_config.NumberColumn(format="PKR %.2f"),
                    "price": st.column_config.NumberColumn(format="PKR %.2f"),
                    "fee": st.column_config.NumberColumn(format="PKR %.2f")
                },
                use_container_width=True
            )
            st.metric("Current Cash Balance", f"PKR {tracker.cash:,.2f}")
        else:
            st.info("No cash transactions recorded.")

    elif page == "Transactions":
        st.header("Transaction History")
        if tracker.transactions:
            trans_df = pd.DataFrame(tracker.transactions)
            trans_df['date'] = trans_df['date'].dt.strftime('%Y-%m-%d')
            st.subheader("Transactions")
            selected = []
            for i, row in trans_df.iterrows():
                cols = st.columns([1, 8])
                with cols[0]:
                    if st.checkbox(f"Delete {i}", key=f"delete_{i}"):
                        selected.append(i)
                with cols[1]:
                    st.write(f"{row['date']} | {row['type']} | {row['ticker']} | Qty: {row['quantity']} | Price: PKR {row['price']:.2f} | Fee: PKR {row['fee']:.2f} | Total: PKR {row['total']:.2f}")
            if st.button("Delete Selected Transactions"):
                try:
                    for index in sorted(selected, reverse=True):
                        tracker.delete_transaction(index)
                    st.success("Selected transactions deleted successfully!")
                    st.experimental_rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")
        else:
            st.info("No transactions recorded.")

    elif page == "Current Prices":
        st.header("Current Prices")
        if st.button("Fetch Latest PSX Data"):
            new_data = fetch_psx_data()
            tracker.current_prices.update(new_data)
            st.success("PSX data fetched and updated!")
        prices_list = [{'Ticker': k, 'Price': v['price'], 'Sharia Compliant': v['sharia']} for k, v in tracker.current_prices.items()]
        prices_df = pd.DataFrame(prices_list)
        edited_df = st.data_editor(prices_df, num_rows="dynamic", use_container_width=True, key="prices_editor")
        if st.button("Update Prices"):
            for _, row in edited_df.iterrows():
                ticker = row['Ticker']
                price = row['Price']
                sharia = row['Sharia Compliant']
                tracker.current_prices[ticker] = {'price': price, 'sharia': sharia}
            st.success("Prices updated successfully!")

    elif page == "Add Transaction":
        st.header("Add Transaction")
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", value=datetime.now())
                ticker = st.selectbox("Ticker", sorted(tracker.current_prices.keys()))
                trans_type = st.selectbox("Type", ["Buy", "Sell", "Deposit"])
            with col2:
                quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
                price = st.number_input("Price", min_value=0.0, step=0.01, value=tracker.current_prices.get(ticker, {'price': 0.0})['price'])
                fee = st.number_input("Fee", min_value=0.0, value=0.0, step=0.01)
            submit = st.form_submit_button("Add Transaction")
            if submit:
                try:
                    tracker.add_transaction(date, ticker if trans_type != "Deposit" else None, trans_type, quantity, price, fee)
                    st.success("Transaction added successfully!")
                    st.experimental_rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

    elif page == "Add Dividend":
        st.header("Add Dividend")
        with st.form("dividend_form"):
            ticker = st.selectbox("Ticker", sorted(tracker.current_prices.keys()))
            amount = st.number_input("Dividend Amount", min_value=0.0, step=0.01)
            submit = st.form_submit_button("Add Dividend")
            if submit:
                try:
                    tracker.add_dividend(ticker, amount)
                    st.success("Dividend added successfully!")
                    st.experimental_rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

if __name__ == '__main__':
    main()
