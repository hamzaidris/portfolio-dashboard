import json

class Tracker:
    def __init__(self, cash=0.0, transactions=None, dividends=None):
        self.cash = cash
        self.transactions = transactions if transactions is not None else []
        self.dividends = dividends if dividends is not None else []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def add_dividend(self, dividend):
        self.dividends.append(dividend)

    def to_dict(self):
        """Convert tracker state into JSON-serializable dict."""
        return {
            "cash": self.cash,
            "transactions": self.transactions,
            "dividends": self.dividends,
        }

    @classmethod
    def from_dict(cls, data):
        """Recreate a Tracker object from dict (safe defaults)."""
        return cls(
            cash=data.get("cash", 0.0),
            transactions=data.get("transactions", []),
            dividends=data.get("dividends", []),
        )

    def __repr__(self):
        return f"<Tracker cash={self.cash} transactions={len(self.transactions)} dividends={len(self.dividends)}>"
