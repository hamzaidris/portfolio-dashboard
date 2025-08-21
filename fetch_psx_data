```python
import requests
import json
from datetime import datetime
import pytz
from retrying import retry
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_working_hours():
    """Check if current time is within PSX working hours (9 AM–5 PM PKT, UTC+5)."""
    now_utc = datetime.now(pytz.UTC)
    pkt_tz = pytz.timezone("Asia/Karachi")
    now_pkt = now_utc.astimezone(pkt_tz)
    hour = now_pkt.hour
    return 9 <= hour < 17

def retry_if_api_fails(exception):
    """Retry if requests exception occurs during working hours."""
    return is_working_hours() and isinstance(exception, requests.RequestException)

@retry(stop_max_attempt_number=3 if is_working_hours() else 1, wait_fixed=2000, retry_on_exception=retry_if_api_fails)
def fetch_psx_data():
    """Fetch stock prices and data from PSX Terminal APIs, fallback to DPS PSX."""
    prices = {}
    fallback_prices = {
        'MLCF': {'price': 83.48, 'sharia': True, 'type': 'Stock'},
        'GCIL': {'price': 26.70, 'sharia': True, 'type': 'Stock'},
        'MEBL': {'price': 374.98, 'sharia': True, 'type': 'Stock'},
        'OGDC': {'price': 272.69, 'sharia': True, 'type': 'Stock'},
        'GAL': {'price': 529.99, 'sharia': True, 'type': 'Stock'},
        'GHNI': {'price': 788.00, 'sharia': True, 'type': 'Stock'},
        'HALEON': {'price': 829.00, 'sharia': True, 'type': 'Stock'},
        'MARI': {'price': 629.60, 'sharia': True, 'type': 'Stock'},
        'GLAXO': {'price': 429.99, 'sharia': True, 'type': 'Stock'},
        'FECTC': {'price': 88.15, 'sharia': True, 'type': 'Stock'},
        'FFC': {'price': 454.10, 'sharia': False, 'type': 'Stock'},
        'MUGHAL': {'price': 64.01, 'sharia': False, 'type': 'Stock'},
        'MUF1': {'price': 150.00, 'sharia': True, 'type': 'Mutual Fund'},
        'COM1': {'price': 2500.00, 'sharia': False, 'type': 'Commodity'}
    }
    try:
        response = requests.get("https://psxterminal.com/api/market-data", timeout=10)
        response.raise_for_status()
        try:
            response_json = response.json()
            if not isinstance(response_json, dict) or not response_json.get("success", False):
                logger.error("Market data API returned unexpected response. Trying DPS PSX.")
                raise requests.RequestException("Invalid response")
            market_data = response_json.get("data", {})
            if isinstance(market_data, dict):
                for market, stocks in market_data.items():
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
                                prices[ticker] = {
                                    "price": float(price),
                                    "sharia": False,  # Default, updated later via /api/yields
                                    "type": "Stock",
                                    "change": item.get("change", 0.0),
                                    "changePercent": item.get("changePercent", 0.0) * 100,  # Convert to percentage
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
            else:
                logger.error(f"Market data 'data' field is not a dict: {type(market_data)}. Trying DPS PSX.")
                raise requests.RequestException("Invalid data field")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse market data API response as JSON: {response.text}. Trying DPS PSX.")
            raise requests.RequestException("JSON decode error")
    except requests.RequestException:
        try:
            response = requests.get("https://dps.psx.com.pk/symbols", timeout=10)
            response.raise_for_status()
            try:
                symbols_data = response.json()
                for item in symbols_data:
                    ticker = item.get("symbol")
                    if ticker:
                        prices[ticker] = {
                            "price": 0.0,
                            "sharia": False,  # Default, updated later or via fallback
                            "type": "Stock",
                            "change": 0.0,
                            "changePercent": 0.0,
                            "volume": 0,
                            "trades": 0,
                            "value": 0.0,
                            "high": 0.0,
                            "low": 0.0,
                            "bid": 0.0,
                            "ask": 0.0,
                            "bidVol": 0,
                            "askVol": 0,
                            "timestamp": datetime.now(pytz.UTC).isoformat()
                        }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse DPS PSX response as JSON: {response.text}. Using fallback prices.")
                return fallback_prices
        except requests.RequestException as e:
            logger.error(f"Error fetching DPS PSX data: {e}. Using fallback prices.")
            return fallback_prices

    if prices:
        for ticker in prices.keys():
            try:
                response = requests.get(f"https://psxterminal.com/api/yields/{ticker}", timeout=10)
                response.raise_for_status()
                try:
                    response_json = response.json()
                    yields_data = response_json.get("data", {})
                    if not isinstance(yields_data, dict):
                        logger.warning(f"Invalid yields data for {ticker}: {yields_data}")
                        continue
                    price = yields_data.get("price")
                    is_non_compliant = yields_data.get("isNonCompliant", True)
                    if price is not None:
                        try:
                            prices[ticker]["price"] = float(price)
                            prices[ticker]["sharia"] = not is_non_compliant
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid price for {ticker}: {price}")
                            continue
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse yields API response for {ticker}: {response.text}")
                    continue
            except requests.RequestException as e:
                logger.warning(f"Error fetching yields data for {ticker}: {e}")
                continue

    return prices or fallback_prices

def save_psx_data():
    """Fetch PSX data and save to psx_data.json."""
    try:
        data = fetch_psx_data()
        output = {
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "data": data
        }
        with open("psx_data.json", "w") as f:
            json.dump(output, f, indent=2)
        logger.info("PSX data fetched and saved to psx_data.json")
    except Exception as e:
        logger.error(f"Failed to fetch and save PSX data: {e}")

if __name__ == "__main__":
    save_psx_data()
```
