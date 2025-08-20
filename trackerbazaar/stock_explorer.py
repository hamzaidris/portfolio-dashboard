import streamlit as st
import pandas as pd
from trackerbazaar.tracker import PortfolioTracker

def render_stock_explorer(tracker):
    st.header("Stock Explorer")
    st.write("Search and explore investment opportunities across stocks, mutual funds, and commodities.")
    prices_df = pd.DataFrame([
        {
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
        }
        for k, v in tracker.current_prices.items()
    ])
    if not prices_df.empty:
        prices_df['Timestamp'] = pd.to_datetime(prices_df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        search_term = st.text_input("Search by Ticker or Name")
        asset_type = st.selectbox("Asset Type", ["All", "Stock", "Mutual Fund", "Commodity", "Bond"])
        sharia_filter = st.checkbox("Show only Sharia-compliant assets", value=False)
        filtered_df = prices_df
        if search_term:
            filtered_df = filtered_df[filtered_df['Ticker'].str.contains(search_term, case=False, na=False)]
        if asset_type != "All":
            filtered_df = filtered_df[filtered_df['Type'] == asset_type]
        if sharia_filter:
            filtered_df = filtered_df[filtered_df['Sharia Compliant'] == '✅']
        if not filtered_df.empty:
            st.dataframe(
                filtered_df,
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
                use_container_width=True
            )
        else:
            st.info("No assets match the search criteria.")
    else:
        st.info("No stock data available. Ensure market-data.json and kmi_shares.txt are present.")
