import json

class Tracker:
    def __init__(self, cash=0.0, transactions=None, dividends=None):
        # Force safe defaults
        self.cash = float(cash) if cash is not None else 0.0
        self.transactions = list(transactions) if transactions is not None else []
        self.dividends = list(dividends) if dividends is not None else []

    def add_transaction(self, transaction: dict):
        """Add a transaction (must be JSON-serializable dict)."""
        if isinstance(transaction, dict):
            self.transactions.append(transaction)
        else:
            self.transactions.append({"value": str(transaction)})

    def add_dividend(self, dividend: dict):
        """Add a dividend (must be JSON-serializable dict)."""
        if isinstance(dividend, dict):
            self.dividends.append(dividend)
        else:
            self.dividends.append({"value": str(dividend)})

    def to_dict(self):
        """Convert tracker state into JSON-safe dict."""
        return {
            "cash": float(self.cash),
            "transactions": self._ensure_json_safe(self.transactions),
            "dividends": self._ensure_json_safe(self.dividends),
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Recreate Tracker from dict (with safe defaults)."""
        if not isinstance(data, dict):
            return cls()
        return cls(
            cash=data.get("cash", 0.0),
            transactions=data.get("transactions", []),
            dividends=data.get("dividends", []),
        )

    def _ensure_json_safe(self, items):
        """Ensure items are JSON serializable (convert non-serializable)."""
        safe = []
        for item in items:
            try:
                json.dumps(item)  # test
                safe.append(item)
            except Exception:
                safe.append(str(item))  # fallback
        return safe

    def __repr__(self):
        return f"<Tracker cash={self.cash} txns={len(self.transactions)} divs={len(self.dividends)}>"
