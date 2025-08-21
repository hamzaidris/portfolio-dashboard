# trackerbazaar/portfolios.py

from trackerbazaar.tracker import PortfolioTracker


class PortfolioManager:
    """
    High-level manager to interact with PortfolioTracker.
    Keeps business logic separate from Streamlit/UI code.
    """

    def __init__(self):
        # Always use PortfolioTracker with trackerbazaar_v2.db
        self.tracker = PortfolioTracker()

    def create_portfolio(self, email: str, name: str):
        return self.tracker.create_portfolio(email, name)

    def list_portfolios(self, email: str):
        return self.tracker.list_portfolios(email)

    def add_transaction(self, portfolio_id: int, date: str, ticker: str,
                        transaction_type: str, quantity: float, price: float, brokerage: float = 0.0):
        return self.tracker.add_transaction(
            portfolio_id, date, ticker, transaction_type, quantity, price, brokerage
        )

    def get_transactions(self, portfolio_id: int):
        return self.tracker.get_transactions(portfolio_id)

    def add_dividend(self, portfolio_id: int, date: str, ticker: str, amount: float):
        return self.tracker.add_dividend(portfolio_id, date, ticker, amount)

    def get_dividends(self, portfolio_id: int):
        return self.tracker.get_dividends(portfolio_id)

    def calculate_portfolio_value(self, portfolio_id: int, current_prices: dict):
        return self.tracker.calculate_portfolio_value(portfolio_id, current_prices)
