# trackerbazaar/portfolios.py
import streamlit as st
from trackerbazaar.tracker import PortfolioTracker

class PortfolioManager:
    def __init__(self):
        if "portfolio_manager" not in st.session_state:
            st.session_state.portfolio_manager = self
        self.portfolios = st.session_state.portfolios

    def create_portfolio(self, name):
        if name not in self.portfolios:
            self.portfolios[name] = PortfolioTracker()
            st.session_state.portfolios = self.portfolios
            return self.portfolios[name]
        return None

    def get_portfolio(self, name):
        return self.portfolios.get(name)

    def get_portfolio_names(self):
        return list(self.portfolios.keys())

    def select_portfolio(self):
        if not self.portfolios:
            st.warning("No portfolios created. Create one first.")
            return None
        return st.sidebar.selectbox("Select Portfolio", self.get_portfolio_names(), key="selected_portfolio")
