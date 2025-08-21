from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
from .data import load_psx_data, get_price

@dataclass
class PortfolioTracker:
    # core state
    transactions: List[Dict[str, Any]] = field(default_factory=list)
    holdings: Dict[str, Dict[str, float]] = field(default_factory=dict)  # sym -> {qty, avg_price, invested}
    dividends: List[Dict[str, Any]] = field(default_factory=list)
    realized_gain: float = 0.0
    cash: float = 0.0
    initial_cash: float = 0.0

    # settings / metadata
    filer_status: str = "Filer"  # for tax calcs (placeholder)
    broker_fee_pct: float = 0.0  # percent of gross for fees (placeholder)

    # prices
    current_prices: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PortfolioTracker":
        tr = PortfolioTracker()
        if not isinstance(d, dict):
            return tr
        for k, v in d.items():
            setattr(tr, k, v)
        # ensure types
        tr.transactions = list(tr.transactions or [])
        tr.holdings = dict(tr.holdings or {})
        tr.dividends = list(tr.dividends or [])
        tr.current_prices = dict(tr.current_prices or {})
        return tr

    # --- operations ---
    def update_filer_status(self, status: str):
        if status in ("Filer", "Non-Filer"):
            self.filer_status = status

    def set_broker_fee_pct(self, pct: float):
        self.broker_fee_pct = max(0.0, float(pct or 0.0))

    def deposit_cash(self, amount: float):
        amount = float(amount or 0.0)
        if amount <= 0:
            return
        self.cash += amount
        self.initial_cash += amount

    def withdraw_cash(self, amount: float):
        amount = float(amount or 0.0)
        if amount <= 0:
            return
        self.cash = max(0.0, self.cash - amount)

    def add_transaction(self, date: str, symbol: str, side: str, qty: float, price: float, fee: float = 0.0):
        symbol = (symbol or "").upper().strip()
        if not symbol or qty <= 0 or price <= 0:
            return
        gross = qty * price
        total_cost = gross + max(0.0, fee)

        if side.lower() == "buy":
            # Update cash & holdings
            self.cash -= total_cost
            pos = self.holdings.get(symbol, {"qty": 0.0, "avg_price": 0.0, "invested": 0.0})
            new_qty = pos["qty"] + qty
            new_invested = pos["invested"] + total_cost
            new_avg = new_invested / new_qty if new_qty > 0 else 0.0
            self.holdings[symbol] = {"qty": new_qty, "avg_price": new_avg, "invested": new_invested}
        else:  # sell
            self.cash += gross - max(0.0, fee)
            pos = self.holdings.get(symbol, {"qty": 0.0, "avg_price": 0.0, "invested": 0.0})
            sell_qty = min(qty, pos["qty"])
            realized = (price - pos["avg_price"]) * sell_qty - max(0.0, fee)
            self.realized_gain += realized
            remaining_qty = pos["qty"] - sell_qty
            if remaining_qty <= 0:
                self.holdings.pop(symbol, None)
            else:
                # reduce invested proportional to qty sold
                ratio = remaining_qty / max(1e-9, pos["qty"])
                self.holdings[symbol] = {
                    "qty": remaining_qty,
                    "avg_price": pos["avg_price"],
                    "invested": pos["invested"] * ratio,
                }

        self.transactions.append({
            "date": date,
            "symbol": symbol,
            "side": side.lower(),
            "qty": qty,
            "price": price,
            "fee": fee,
            "gross": gross,
            "total_cost": total_cost if side.lower() == "buy" else gross - max(0.0, fee),
        })

    def add_dividend(self, date: str, symbol: str, amount: float):
        self.cash += max(0.0, amount or 0.0)
        self.dividends.append({"date": date, "symbol": (symbol or '').upper(), "amount": float(amount or 0.0)})

    def market_value(self) -> float:
        value = 0.0
        for sym, pos in (self.holdings or {}).items():
            p = get_price(sym, self.current_prices) or pos.get("avg_price", 0.0)
            value += (pos.get("qty", 0.0) * p)
        return value

    def total_invested(self) -> float:
        return sum((pos.get("invested", 0.0) for pos in (self.holdings or {}).values()), 0.0)

def initialize_tracker(tracker: PortfolioTracker, project_root=None):
    """Ensure tracker has current_prices populated and basic defaults."""
    if not tracker.current_prices:
        tracker.current_prices = load_psx_data(project_root=project_root)
    # guarantee other defaults
    tracker.filer_status = tracker.filer_status or "Filer"
    tracker.broker_fee_pct = float(tracker.broker_fee_pct or 0.0)
    return tracker
