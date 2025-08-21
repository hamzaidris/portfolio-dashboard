import os, json
from datetime import datetime, timezone

def _read_json(paths):
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            continue
    return {}

def _read_lines(paths):
    lines = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s:
                        lines.append(s)
            return lines
        except Exception:
            continue
    return lines

def load_psx_data(project_root=None):
    """Return a dict: {symbol: {price: float, sharia: bool, ...}}"""
    here = os.path.dirname(__file__)
    roots = [project_root or os.path.dirname(here), here]
    json_paths = [os.path.join(r, "market-data.json") for r in roots]
    kmi_paths  = [os.path.join(r, "kmi_shares.txt") for r in roots]

    raw = _read_json(json_paths) or {}
    sharia_list = set([x.strip().upper() for x in _read_lines(kmi_paths)])

    data = {}
    data_section = raw.get("data") if isinstance(raw, dict) else {}
    if isinstance(data_section, dict):
        for _mkt, stocks in data_section.items():
            if not isinstance(stocks, dict):
                continue
            for sym, item in stocks.items():
                if not isinstance(item, dict):
                    continue
                price = item.get("price")
                try:
                    price = float(price)
                except Exception:
                    continue
                ts = item.get("timestamp")
                if ts:
                    try:
                        dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
                        iso_ts = dt.isoformat()
                    except Exception:
                        iso_ts = datetime.now(timezone.utc).isoformat()
                else:
                    iso_ts = datetime.now(timezone.utc).isoformat()

                data[sym.upper()] = {
                    "price": price,
                    "change": item.get("change"),
                    "changePercent": item.get("changePercent"),
                    "volume": item.get("volume", 0),
                    "trades": item.get("trades", 0),
                    "value": item.get("value", 0),
                    "high": item.get("high", 0),
                    "low": item.get("low", 0),
                    "timestamp": iso_ts,
                    "sharia": sym.upper() in sharia_list,
                }
    return data

def get_price(symbol, prices):
    if not symbol:
        return None
    return (prices or {}).get(symbol.upper(), {}).get("price")
