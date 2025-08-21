import json
from datetime import datetime

class Tracker:
    def __init__(self):
        # Stores transactions, dividends, and cash movements
        self.transactions = []
        self.dividends = []
        self.cash_movements = []
        self.created_at = datetime.utcnow().isoformat()

    def add_transaction(self, ticker, quantity, price, date=None):
        if not date:
            date = datetime.utcnow().isoformat()
        self.transactions.append({
            "ticker": ticker,
            "quantity": quantity,
            "price": price,
            "date": date
        })

    def add_dividend(self, ticker, amount, date=None):
        if not date:
            date = datetime.utcnow().isoformat()
        self.dividends.append({
            "ticker": ticker,
            "amount": amount,
            "date": date
        })

    def add_cash(self, amount, reason="Deposit", date=None):
        if not date:
            date = datetime.utcnow().isoformat()
        self.cash_movements.append({
            "amount": amount,
            "reason": reason,
            "date": date
        })

    def to_dict(self):
        """
        Convert tracker state into a JSON-safe dict
        """
        return {
            "transactions": self.transactions,
            "dividends": self.dividends,
            "cash_movements": self.cash_movements,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """
        Rebuild tracker object from dict (loaded from DB JSON)
        """
        tracker = cls()
        tracker.transactions = data.get("transactions", [])
        tracker.dividends = data.get("dividends", [])
        tracker.cash_movements = data.get("cash_movements", [])
        tracker.created_at = data.get("created_at", datetime.utcnow().isoformat())
        return tracker
