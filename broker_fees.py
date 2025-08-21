import streamlit as st
from trackerbazaar.tracker import PortfolioTracker
from trackerbazaar.portfolios import PortfolioManager

def render_broker_fees(tracker):
    portfolio_manager = PortfolioManager()
    email = st.session_state.get('logged_in_user')
    portfolio_name = st.session_state.get('selected_portfolio')

    st.header("Broker Fees")
    st.write("Define your broker fees for distribution calculations.")
    with st.form("broker_fees_form"):
        low_price_fee = st.number_input("Low Price Fee (P <= 20)", min_value=0.0, value=tracker.broker_fees.get('low_price_fee', 0.03), step=0.01)
        sst_low_price = st.number_input("SST for Low Price (P <= 20)", min_value=0.0, value=tracker.broker_fees.get('sst_low_price', 0.0045), step=0.0001)
        brokerage_rate = st.number_input("Brokerage Rate (P > 20)", min_value=0.0, value=tracker.broker_fees.get('brokerage_rate', 0.0015), step=0.0001)
        sst_rate = st.number_input("SST Rate for Brokerage", min_value=0.0, value=tracker.broker_fees.get('sst_rate', 0.15), step=0.01)
        submit = st.form_submit_button("Update Broker Fees")
        if submit:
            tracker.broker_fees = {
                'low_price_fee': low_price_fee,
                'sst_low_price': sst_low_price,
                'brokerage_rate': brokerage_rate,
                'sst_rate': sst_rate
            }
            portfolio_manager.save_portfolio(portfolio_name, email, tracker)
            st.session_state.data_changed = True
            st.success("Broker fees updated successfully!")
