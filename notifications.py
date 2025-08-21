import streamlit as st
import pandas as pd
from trackerbazaar.tracker import PortfolioTracker

def render_notifications(tracker):
    st.header("Notifications")
    st.write("Real-time alerts for price movements, trades, and portfolio updates.")
    alerts_df = tracker.get_alerts()
    if not alerts_df.empty:
        alerts_df['date'] = pd.to_datetime(alerts_df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(alerts_df, use_container_width=True)
    else:
        st.info("No notifications available. Add transactions to generate alerts.")
