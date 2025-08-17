import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def excel_date_to_datetime(serial):
    """Convert Excel serial date to Python datetime."""
    try:
        return datetime(1900, 1, 1) + timedelta(days=int(serial) - 2)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Excel serial date: {serial}")

class PortfolioTracker:
    def __init__(self):
        self.transactions = []
        self.holdings = {}  # ticker: {'shares': float, 'total_cost': float}
        self.dividends = {}  # ticker: total_dividends
        self.realized_gain = 0.0
        self.cash = 0.0
        self.initial_cash = 0.0
        # Prices from PSX_Live_Price_fetch_python sheet
        self.current_prices = {
            'MLCF': 83.19,
            'GCIL': 26.58,
            'MEBL': 369.99,
            'OGDC': 270.48,
            'GAL': 525.88,
            'GHNI': 787.05,
            'MUGHAL': 63.76,
            'HALEON': 822.04,
            'MARI': 618.53,
            'GLAXO': 425.6,
            'FECTC': 84.61
        }

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
            self.cash += quantity  # quantity as amount
            self.initial_cash += quantity  # track total deposits
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
        self.cash += amount  # assume dividend adds to cash

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
                            self.current_prices.get(ticker, 0.0)
            if current_price == 0.0:
                st.warning(f"No price available for {ticker}. Using 0.0.")
            market_value = shares * current_price
            total_portfolio_value += market_value
            gain_loss = market_value - h['total_cost']
            per_gain = gain_loss / h['total_cost'] if h['total_cost'] > 0 else 0.0
            div = self.dividends.get(ticker, 0.0)
            roi = (market_value + div) / h['total_cost'] * 100 if h['total_cost'] > 0 else 0.0
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
                'ROI %': round(roi, 2)
            })
        portfolio_df = pd.DataFrame(portfolio)
        if total_portfolio_value > 0:
            portfolio_df['Allocation %'] = (portfolio_df['Market Value'] / total_portfolio_value * 100).round(2)
        return portfolio_df.sort_values(by='Market Value', ascending=False)

    def get_dashboard(self, current_prices=None):
        """Generate dashboard summary metrics."""
        portfolio_df = self.get_portfolio(current_prices)
        total_portfolio_value = portfolio_df['Market Value'].sum()
        total_unrealized = portfolio_df['Gain/Loss'].sum()
        total_dividends = sum(self.dividends.values())
        total_invested = self.initial_cash - self.cash
        total_roi = (total_portfolio_value + total_dividends) / sum(h['total_cost'] for h in self.holdings.values()) * 100 if self.holdings else 0.0
        return {
            'Total Realized Gain': round(self.realized_gain, 2),
            'Total Portfolio Value': round(total_portfolio_value, 2),
            'Total Unrealized Gain': round(total_unrealized, 2),
            'Total Dividends': round(total_dividends, 2),
            'Total Invested': round(total_invested, 2),
            'Total ROI %': round(total_roi, 2),
            'Cash Balance': round(self.cash, 2)
        }

def initialize_tracker(tracker):
    """Initialize tracker with transactions and dividends from Excel."""
    tracker.add_transaction(datetime(2025, 1, 1), None, 'Deposit', 414375.28, 0)
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
    page = st.sidebar.radio("Go to", ["Portfolio", "Add Transaction", "Add Dividend", "Transactions"])

    if page == "Portfolio":
        st.header("Portfolio Summary")
        portfolio_df = tracker.get_portfolio()
        if not portfolio_df.empty:
            # Display metrics
            dashboard = tracker.get_dashboard()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Portfolio Value", f"PKR {dashboard['Total Portfolio Value']:,.2f}")
            col2.metric("Total ROI %", f"{dashboard['Total ROI %']:.2f}%")
            col3.metric("Total Dividends", f"PKR {dashboard['Total Dividends']:,.2f}")
            col4.metric("Cash Balance", f"PKR {dashboard['Cash Balance']:,.2f}")

            # Portfolio table
            st.dataframe(
                portfolio_df,
                column_config={
                    "Market Value": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Total Invested": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Gain/Loss": st.column_config.NumberColumn(format="PKR %.2f"),
                    "Dividends": st.column_config.NumberColumn(format="PKR %.2f"),
                    "% Gain": st.column_config.NumberColumn(format="%.2f%"),
                    "ROI %": st.column_config.NumberColumn(format="%.2f%"),
                    "Allocation %": st.column_config.NumberColumn(format="%.2f%")
                },
                use_container_width=True
            )

            # Allocation pie chart
            fig = px.pie(
                portfolio_df,
                values='Market Value',
                names='Stock',
                title='Portfolio Allocation',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No holdings in portfolio.")

    elif page == "Add Transaction":
        st.header("Add Transaction")
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", value=datetime.now())
                ticker = st.selectbox("Ticker", list(tracker.current_prices.keys()) + ["None (for Deposit)"])
                trans_type = st.selectbox("Type", ["Buy", "Sell", "Deposit"])
            with col2:
                quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
                price = st.number_input("Price", min_value=0.0, step=0.01)
                fee = st.number_input("Fee", min_value=0.0, value=0.0, step=0.01)
            submit = st.form_submit_button("Add Transaction")
            if submit:
                try:
                    tracker.add_transaction(date, ticker if trans_type != "Deposit" else None, trans_type, quantity, price, fee)
                    st.success("Transaction added successfully!")
                except ValueError as e:
                    st.error(f"Error: {e}")

    elif page == "Add Dividend":
        st.header("Add Dividend")
        with st.form("dividend_form"):
            ticker = st.selectbox("Ticker", list(tracker.current_prices.keys()))
            amount = st.number_input("Dividend Amount", min_value=0.0, step=0.01)
            submit = st.form_submit_button("Add Dividend")
            if submit:
                try:
                    tracker.add_dividend(ticker, amount)
                    st.success("Dividend added successfully!")
                except ValueError as e:
                    st.error(f"Error: {e}")

    elif page == "Transactions":
        st.header("Transaction History")
        if tracker.transactions:
            trans_df = pd.DataFrame(tracker.transactions)
            trans_df['date'] = trans_df['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(
                trans_df,
                column_config={
                    "total": st.column_config.NumberColumn(format="PKR %.2f"),
                    "realized": st.column_config.NumberColumn(format="PKR %.2f"),
                    "price": st.column_config.NumberColumn(format="PKR %.2f"),
                    "fee": st.column_config.NumberColumn(format="PKR %.2f")
                },
                use_container_width=True
            )
        else:
            st.info("No transactions recorded.")

if __name__ == '__main__':
    main()