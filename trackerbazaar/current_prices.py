# trackerbazaar/portfolio.py

from trackerbazaar.tracker import PortfolioTracker
from trackerbazaar.current_prices import CurrentPrices  # ✅ fixed

class Portfolio:
    def __init__(self, name):
        self.name = name
        self.tracker = PortfolioTracker()
        self.price_service = CurrentPrices()   # ✅ instantiate

    def get_summary(self):
        holdings = self.tracker.get_holdings(self.name)
        summary = {"holdings": [], "total_value": 0}

        for holding in holdings:
            ticker = holding["ticker"]
            qty = holding["quantity"]
            avg_price = holding["avg_price"]

            current_price = self.price_service.get_price(ticker)
            value = qty * current_price
            profit_loss = (current_price - avg_price) * qty

            summary["holdings"].append({
                "ticker": ticker,
                "quantity": qty,
                "avg_price": avg_price,
                "current_price": current_price,
                "value": value,
                "profit_loss": profit_loss,
            })

            summary["total_value"] += value

        return summary
