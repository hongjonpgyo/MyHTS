from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict

from backend_binance_old.db.database import get_db
from backend_binance_old.models.order_model import Order
from backend_binance_old.services.market.market_service import market_service
from backend_binance_old.services.symbol_service import is_futures

router = APIRouter(prefix="/orderbook/futures", tags=["Orderbook-Futures"])


@router.get("/{symbol}/{account_id}")
def get_futures_orderbook(symbol: str, account_id: int, db: Session = Depends(get_db)):
    symbol = symbol.upper()

    if not is_futures(symbol):
        raise HTTPException(400, "Not futures symbol")

    # 1️⃣ 기준 가격 (Yahoo / last)
    price_info = market_service.get_price(symbol)
    if not price_info or "last" not in price_info:
        raise HTTPException(500, "No futures price")

    mid = float(price_info["last"])

    # 2️⃣ 내부 LIMIT OPEN 주문
    orders = (
        db.query(Order)
        .filter(
            Order.symbol.has(symbol_code=symbol),
            Order.order_type == "LIMIT",
            Order.status == "OPEN",
        )
        .all()
    )

    bids = defaultdict(lambda: {"all_qty": 0, "all_cnt": 0, "my_qty": 0, "my_cnt": 0})
    asks = defaultdict(lambda: {"all_qty": 0, "all_cnt": 0, "my_qty": 0, "my_cnt": 0})

    for o in orders:
        price = float(o.request_price)
        side_map = bids if o.side == "BUY" else asks

        side_map[price]["all_qty"] += float(o.qty)
        side_map[price]["all_cnt"] += 1

        if o.account_id == account_id:
            side_map[price]["my_qty"] += float(o.qty)
            side_map[price]["my_cnt"] += 1

    # 3️⃣ 정렬
    bid_rows = sorted(bids.items(), key=lambda x: x[0], reverse=True)
    ask_rows = sorted(asks.items(), key=lambda x: x[0])

    return {
        "symbol": symbol,
        "mid": mid,
        "bids": [
            {
                "price": p,
                **v
            } for p, v in bid_rows
        ],
        "asks": [
            {
                "price": p,
                **v
            } for p, v in ask_rows
        ],
    }
