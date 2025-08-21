import datetime


class Tracker:
    def __init__(self):
        self.transactions = []
        self.dividends = []
        self.cash_balance = 0.0
        self.created_at = datetime.datetime.now().isoformat()

    def add_transaction(self, date, ticker, quantity, price, fees=0.0, tx_type="BUY"):
        """Add a buy or sell transaction"""
        tx = {
            "date": date,
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "fees": fees,
            "type": tx_type.upper()
        }
        self.transactions.append(tx)

    def add_dividend(self, date, ticker, amount):
        """Record a dividend payout"""
        div = {
            "date": date,
            "ticker": ticker,
            "amount": amount
        }
        self.dividends.append(div)

    def add_cash(self, amount):
        """Deposit or withdraw cash"""
        self.cash_balance += amount

    def portfolio_value(self, current_prices):
        """Calculate total portfolio value from current prices"""
        value = self.cash_balance
        for tx in self.transactions:
            ticker = tx["ticker"]
            qty = tx["quantity"] if tx["type"] == "BUY" else -tx["quantity"]
            price = current_prices.get(ticker, tx["price"])
            value += qty * price
        return value

    def to_dict(self):
        """Convert Tracker to dictionary for saving"""
        return {
            "transactions": self.transactions,
            "dividends": self.dividends,
            "cash_balance": self.cash_balance,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild Tracker from a saved dictionary"""
        tracker = cls()
        tracker.transactions = data.get("transactions", [])
        tracker.dividends = data.get("dividends", [])
        tracker.cash_balance = data.get("cash_balance", 0.0)
        tracker.created_at = data.get("created_at", datetime.datetime.now().isoformat())
        return tracker
