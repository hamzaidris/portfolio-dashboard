import streamlit as st
import pandas as pd
from datetime import datetime
from trackerbazaar.tracker import PortfolioTracker

def render_current_prices(tracker):
    st.header("Current Prices")
    prices_list = [{
        'Ticker': k,
        'Price': v['price'],
        'Sharia Compliant': '✅' if v['sharia'] else '❌',
        'Type': v.get('type', 'Stock'),
        'Change': v.get('change', 0.0),
        'Change %': v.get('changePercent', 0.0),
        'Volume': v.get('volume', 0),
        'Trades': v.get('trades', 0),
        'Value': v.get('value', 0.0),
        'High': v.get('high', 0.0),
        'Low': v.get('low', 0.0),
        'Bid': v.get('bid', 0.0),
        'Ask': v.get('ask', 0.0),
        'Bid Volume': v.get('bidVol', 0),
        'Ask Volume': v.get('askVol', 0),
        'Timestamp': v.get('timestamp', datetime.now())
    } for k, v in tracker.current_prices.items()]
    prices_df = pd.DataFrame(prices_list)
    if not prices_df.empty:
        prices_df['Timestamp'] = pd.to_datetime(prices_df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        edited_df = st.data_editor(
            prices_df,
            column_config={
                "Price": st.column_config.NumberColumn(format="PKR %.2f"),
                "Change": st.column_config.NumberColumn(format="PKR %.2f"),
                "Change %": st.column_config.NumberColumn(format="%.2f%"),
                "Value": st.column_config.NumberColumn(format="PKR %.2f"),
                "High": st.column_config.NumberColumn(format="PKR %.2f"),
                "Low": st.column_config.NumberColumn(format="PKR %.2f"),
                "Bid": st.column_config.NumberColumn(format="PKR %.2f"),
                "Ask": st.column_config.NumberColumn(format="PKR %.2f"),
                "Sharia Compliant": st.column_config.TextColumn(
                    "Sharia Compliant",
                    help="✅ = Sharia Compliant, ❌ = Non-Compliant"
                )
            },
            num_rows="dynamic",
            use_container_width=True,
            key="prices_editor"
        )
        if st.button("Update Prices"):
            updated_prices = {}
            for _, row in edited_df.iterrows():
                ticker = row['Ticker']
                updated_prices[ticker] = {
                    'price': row['Price'],
                    'sharia': row['Sharia Compliant'] == '✅',
                    'type': row['Type'],
                    'change': row['Change'],
                    'changePercent': row['Change %'] / 100,
                    'volume': row['Volume'],
                    'trades': row['Trades'],
                    'value': row['Value'],
                    'high': row['High'],
                    'low': row['Low'],
                    'bid': row['Bid'],
                    'ask': row['Ask'],
                    'bidVol': row['Bid Volume'],
                    'askVol': row['Ask Volume'],
                    'timestamp': pd.to_datetime(row['Timestamp']).timestamp()
                }
            tracker.current_prices = updated_prices
            st.session_state.data_changed = True
            st.success("Prices updated successfully!")
