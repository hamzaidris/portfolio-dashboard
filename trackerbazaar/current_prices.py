# trackerbazaar/current_prices.py

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "market-data.json")

class CurrentPrices:
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self._load_prices()

    def _load_prices(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.prices = json.load(f)
        else:
            self.prices = {}

    def get_price(self, ticker: str) -> float:
        """Return the current price of a stock (defaults to 0 if missing)."""
        return float(self.prices.get(ticker, 0.0))
