import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import pytz
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)  # Cache for 1 hour, reload if files change
def load_psx_data():
    """Load stock data from market-data.json and Sharia compliance from kmi_shares.txt."""
    sharia_compliant = set()
    try:
        with open("kmi_shares.txt", "r") as f:
            sharia_compliant = {line.strip() for line in f if line.strip()}
        logger.info(f"Loaded {len(sharia_compliant)} Sharia-compliant stocks from kmi_shares.txt")
    except FileNotFoundError:
        logger.error("kmi_shares.txt not found. Returning empty data.")
        st.warning("kmi_shares.txt not found. Please ensure the file is present.")
        return {}
    except Exception as e:
        logger.error(f"Error reading kmi_shares.txt: {e}. Returning empty data.")
        st.warning(f"Error reading kmi_shares.txt: {e}. Please check the file.")
        return {}

    try:
        with open("market-data.json", "r") as f:
            market_data = json.load(f)
        if not isinstance(market_data, dict) or not market_data.get("success", False):
            logger.error("Invalid market-data.json format. Returning empty data.")
            st.warning("Invalid market-data.json format. Please check the file.")
            return {}
        
        market_data_content = market_data.get("data", {})
        if not isinstance(market_data_content, dict):
            logger.error(f"Market data 'data' field is not a dict: {type(market_data_content)}. Returning empty data.")
            st.warning("Invalid market-data.json structure. Please check the file.")
            return {}

        prices = {}
        for market, stocks in market_data_content.items():
            if not isinstance(stocks, dict):
                logger.warning(f"Skipping invalid market data for {market}: {stocks}")
                continue
            for ticker, item in stocks.items():
                if not isinstance(item, dict):
                    logger.warning(f"Skipping invalid stock data for {ticker}: {item}")
                    continue
                price = item.get("price")
                if ticker and price is not None:
                    try:
                        sharia_name = next((name for name in sharia_compliant if ticker in name or name.lower().replace(" ", "") == ticker.lower()), ticker)
                        is_sharia = sharia_name in sharia_compliant
                        prices[ticker] = {
                            "price": float(price),
                            "sharia": is_sharia,
                            "type": "Stock" if market == "REG" else "Bond" if market == "BNB" else item.get("type", "Stock"),
                            "change": item.get("change", 0.0),
                            "changePercent": item.get("changePercent", 0.0) * 100,
                            "volume": item.get("volume", 0),
                            "trades": item.get("trades", 0),
                            "value": item.get("value", 0.0),
                            "high": item.get("high", 0.0),
                            "low": item.get("low", 0.0),
                            "bid": item.get("bid", 0.0),
                            "ask": item.get("ask", 0.0),
                            "bidVol": item.get("bidVol", 0),
                            "askVol": item.get("askVol", 0),
                            "timestamp": datetime.fromtimestamp(item.get("timestamp", 0)).isoformat() if item.get("timestamp") else datetime.now(pytz.UTC).isoformat()
                        }
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid price for {ticker}: {price}")
                        continue

        logger.info(f"Loaded {len(prices)} tickers from market-data.json")
        if not prices:
            st.warning("No valid data in market-data.json. Please check the file.")
            return {}
        st.info(f"Loaded {len(prices)} tickers from market-data.json")
        return prices
    except FileNotFoundError:
        logger.error("market-data.json not found. Returning empty data.")
        st.warning("market-data.json not found. Please ensure the file is present.")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding market-data.json: {e}. Returning empty data.")
        st.warning(f"Error decoding market-data.json: {e}. Please check the file.")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading market-data.json: {e}. Returning empty data.")
        st.warning(f"Unexpected error loading market-data.json: {e}. Please check the file.")
        return {}

def excel_date_to_datetime(serial):
    """Convert Excel serial date to Python datetime."""
    try:
        return datetime(1900, 1, 1) + timedelta(days=int(serial) - 2)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid Excel serial date: {serial}")
