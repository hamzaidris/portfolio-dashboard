# trackerbazaar/portfolios.py

from trackerbazaar.tracker import PortfolioTracker


class PortfolioManager:
    def __init__(self):
        # Create a tracker instance
        self.tracker = PortfolioTracker()

    def get_all_portfolios(self, owner_email=None):
        """
        Get all portfolios. 
        If owner_email is provided, only return that user’s portfolios.
        """
        return self.tracker.list_portfolios(owner_email=owner_email)

    # ✅ Backward compatibility (so old calls to list_portfolios still work)
    def list_portfolios(self, owner_email=None):
        return self.get_all_portfolios(owner_email)

    def create_portfolio(self, name, owner_email):
        """
        Create a new portfolio for a given user.
        """
        return self.tracker.create_portfolio(name, owner_email)

    def delete_portfolio(self, portfolio_id):
        """
        Delete a portfolio by its ID.
        """
        return self.tracker.delete_portfolio(portfolio_id)
