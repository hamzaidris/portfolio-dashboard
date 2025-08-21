from trackerbazaar.portfolios import PortfolioManager
from trackerbazaar.users import UserManager
import streamlit as st


def main():
    st.set_page_config(page_title="TrackerBazaar", layout="wide")

    user_manager = UserManager()
    portfolio_manager = PortfolioManager(db_path="trackerbazaar_v2.db")  # NEW DB

    current_user = user_manager.get_current_user()
    ...
