# trackerbazaar/portfolios.py

from trackerbazaar.tracker import PortfolioTracker

class PortfolioManager:
    def __init__(self):
        self.tracker = PortfolioTracker()

    def get_all_portfolios(self, owner_email=None):
        """
        Get all portfolios. If owner_email is passed, return only their portfolios.
        """
        return self.tracker.list_portfolios(owner_email=owner_email)

    def create_portfolio(self, name, owner_email):
        """
        Create a new portfolio for a given user.
        """
        return self.tracker.create_portfolio(name, owner_email)

    def delete_portfolio(self, portfolio_id):
        """
        Delete a portfolio by ID.
        """
        return self.tracker.delete_portfolio(portfolio_id)
