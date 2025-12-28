from collections import defaultdict
from typing import Dict, List
from sqlalchemy.orm import Session

from backend.models.order_model import Order
from backend.models.symbol_model import Symbol
from backend.services.market.market_service import market_service


def normalize_price(price: float, tick: float) -> float:
    return round(round(price / tick) * tick, 8)


def build_synthetic_orderbook(
    *,
    db: Session,
    symbol_code: str,
    account_id: int,
    depth: int = 20,
) -> Dict[str, List[dict]]:

    symbol_code = symbol_code.upper()

    # -------------------------------------------------
    # 1️⃣ Symbol 모델
    # -------------------------------------------------
    symbol = (
        db.query(Symbol)
        .filter(Symbol.symbol_code == symbol_code)
        .first()
    )
    if not symbol:
        raise Exception(f"Symbol not found: {symbol_code}")

    # -------------------------------------------------
    # 2️⃣ 기준 가격
    # -------------------------------------------------
    price_info = market_service.get_price(symbol_code)
    if not price_info:
        raise Exception(f"No price cache for {symbol_code}")

    mid = float(price_info["last"])
    tick = float(symbol.tick_size or 1.0)

    # -------------------------------------------------
    # 3️⃣ 내부 LIMIT 주문 집계
    # -------------------------------------------------
    orders = (
        db.query(Order)
        .filter(
            Order.symbol_id == symbol.symbol_id,
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
        price = normalize_price(float(o.request_price), tick)
        qty = float(o.qty)

        db_all_qty[price] += qty
        db_all_count[price] += 1

        if o.account_id == account_id:
            db_my_qty[price] += qty
            db_my_count[price] += 1

    # -------------------------------------------------
    # 4️⃣ Synthetic Ladder
    # -------------------------------------------------
    bids, asks = [], []

    for i in range(1, depth + 1):
        bid_price = normalize_price(mid - tick * i, tick)
        ask_price = normalize_price(mid + tick * i, tick)

        bids.append({
            "price": bid_price,
            "binance_qty": 0.0,
            "db_all_qty": db_all_qty.get(bid_price, 0.0),
            "db_all_count": db_all_count.get(bid_price, 0),
            "db_my_qty": db_my_qty.get(bid_price, 0.0),
            "db_my_count": db_my_count.get(bid_price, 0),
        })

        asks.append({
            "price": ask_price,
            "binance_qty": 0.0,
            "db_all_qty": db_all_qty.get(ask_price, 0.0),
            "db_all_count": db_all_count.get(ask_price, 0),
            "db_my_qty": db_my_qty.get(ask_price, 0.0),
            "db_my_count": db_my_count.get(ask_price, 0),
        })

    return {
        "bids": bids,
        "asks": asks,
        "mid": mid,
    }
