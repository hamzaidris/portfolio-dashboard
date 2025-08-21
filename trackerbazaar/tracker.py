import json
from datetime import datetime

class PortfolioTracker:
    def __init__(self, name: str):
        self.name = name
        self.transactions = []   # list of dicts
        self.cash_balance = 0.0  # starting cash
        self.holdings = {}       # symbol → quantity

    def add_transaction(self, symbol: str, qty: int, price: float,
                        t_type: str = "buy", fee: float = 0.0, date: str = None):
        """Add a transaction and update holdings."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        tx = {
            "symbol": symbol,
            "quantity": qty,
            "price": price,
            "type": t_type,
            "fee": fee,
            "date": date
        }
        self.transactions.append(tx)

        # Update holdings
        if t_type == "buy":
            self.holdings[symbol] = self.holdings.get(symbol, 0) + qty
            self.cash_balance -= (qty * price + fee)
        elif t_type == "sell":
            self.holdings[symbol] = self.holdings.get(symbol, 0) - qty
            self.cash_balance += (qty * price - fee)

    def add_cash(self, amount: float):
        self.cash_balance += amount

    def portfolio_value(self, current_prices: dict = None) -> float:
        """Calculate current value given current_prices {symbol: price}."""
        total = self.cash_balance
        if current_prices:
            for sym, qty in self.holdings.items():
                total += qty * current_prices.get(sym, 0)
        return total

    # --------- Persistence helpers ---------
    def to_dict(self) -> dict:
        """Serialize portfolio to dictionary (for JSON saving)."""
        return {
            "name": self.name,
            "transactions": self.transactions,
            "cash_balance": self.cash_balance,
            "holdings": self.holdings
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Rebuild PortfolioTracker from dictionary."""
        tracker = cls(data.get("name", "Untitled"))
        tracker.transactions = data.get("transactions", [])
        tracker.cash_balance = data.get("cash_balance", 0.0)
        tracker.holdings = data.get("holdings", {})
        return tracker

    def __repr__(self):
        return f"<PortfolioTracker {self.name} | Holdings: {self.holdings} | Cash: {self.cash_balance}>"
