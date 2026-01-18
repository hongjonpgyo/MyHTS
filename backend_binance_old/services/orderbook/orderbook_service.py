from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.orm import Session
import requests

from backend_binance_old.config.settings import ORDERBOOK_DEPTH
from backend_binance_old.config.settings import BINANCE_DEPTH_URL
from backend_binance_old.config.symbol_registry import SYMBOL_REGISTRY
from backend_binance_old.models import Symbol
from backend_binance_old.models.order_model import Order
from backend_binance_old.services.market.market_service import market_service
from backend_binance_old.config.futures_meta import FUTURES_META
from backend_binance_old.services.orderbook.synthetic_orderbook import build_synthetic_orderbook


def is_futures(symbol: str) -> bool:
    return symbol.upper() in FUTURES_META


def get_orderbook(symbol: str, account_id: int, db: Session):
    symbol = symbol.upper()

    meta = SYMBOL_REGISTRY.get(symbol)
    if not meta:
        raise HTTPException(404, "Unknown symbol")

    # =================================
    # 1️⃣ Futures → Synthetic Orderbook
    # =================================
    if is_futures(symbol):
        price = market_service.get_price(symbol)
        if not price:
            return {"bids": [], "asks": []}

        last = price["last"]
        return build_synthetic_orderbook(db=db, symbol_code=symbol, account_id=account_id)

    # =================================
    # 2️⃣ Binance → 실제 Merge Orderbook
    # =================================
    depth = requests.get(
        BINANCE_DEPTH_URL,
        params={"symbol": symbol, "limit": ORDERBOOK_DEPTH*2},
        timeout=2,
    ).json()

    bin_bids = [(float(p), float(q)) for p, q in depth.get("bids", [])]
    bin_asks = [(float(p), float(q)) for p, q in depth.get("asks", [])]

    orders = (
        db.query(Order)
        .filter(
            Order.symbol.has(symbol_code=symbol),
            Order.order_type == "LIMIT",
            Order.status == "OPEN",
        )
        .all()
    )

    db_all_qty = defaultdict(float)
    db_all_count = defaultdict(int)
    db_my_qty = defaultdict(float)
    db_my_count = defaultdict(int)

    for o in orders:
        price = float(o.request_price)
        qty = float(o.qty)

        db_all_qty[price] += qty
        db_all_count[price] += 1

        if o.account_id == account_id:
            db_my_qty[price] += qty
            db_my_count[price] += 1

    def merge_side(bin_side):
        out = []
        for price, bin_qty in bin_side:
            out.append({
                "price": price,
                "binance_qty": bin_qty,
                "db_all_qty": db_all_qty.get(price, 0.0),
                "db_all_count": db_all_count.get(price, 0),
                "db_my_qty": db_my_qty.get(price, 0.0),
                "db_my_count": db_my_count.get(price, 0),
            })
        return out

    return {
        "bids": merge_side(bin_bids),
        "asks": merge_side(bin_asks),
    }
