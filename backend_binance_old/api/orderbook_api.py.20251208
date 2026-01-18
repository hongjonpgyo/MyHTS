# backend/api/orderbook_api.py
import requests
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.order_model import Order
from backend.models.symbol_model import Symbol
from backend.config.settings import PRICE_TOLERANCE

router = APIRouter(prefix="/orderbook", tags=["Orderbook"])

BINANCE_DEPTH_URL = "https://api.binance.com/api/v3/depth"


@router.get("/{symbol_code}")
def get_merged_orderbook(symbol_code: str, db: Session = Depends(get_db)):
    """
    Binance 가격 레벨 + 내부 주문 수량으로 오더북 생성

    - Price: Binance depth price
    - Bid/Ask: 우리 orders 테이블의 수량 합
    """

    # 1) symbol_id 찾기
    symbol = (
        db.query(Symbol)
        .filter(Symbol.symbol_code == symbol_code.upper())
        .first()
    )
    if not symbol:
        raise HTTPException(404, detail="Symbol not found")
    symbol_id = symbol.symbol_id

    # 2) Binance depth 가져오기 (가격 레벨용)
    try:
        r = requests.get(
            BINANCE_DEPTH_URL,
            params={"symbol": symbol_code.upper(), "limit": 15},
            timeout=1.5,
        )
        r.raise_for_status()
        depth = r.json()
    except Exception as e:
        raise HTTPException(500, detail=f"Binance depth error: {e}")

    bin_bids = [(float(p), float(q)) for p, q in depth.get("bids", [])]
    bin_asks = [(float(p), float(q)) for p, q in depth.get("asks", [])]

    # 3) 내부 OPEN LIMIT 주문 집계
    orders = (
        db.query(Order)
        .filter(
            Order.symbol_id == symbol_id,
            Order.order_type == "LIMIT",
            Order.status == "OPEN",
        )
        .all()
    )

    my_bids = defaultdict(float)  # price -> 총 qty
    my_asks = defaultdict(float)

    for o in orders:
        price = float(o.request_price)
        qty = float(o.qty)
        if o.side == "BUY":
            my_bids[price] += qty
        elif o.side == "SELL":
            my_asks[price] += qty

    # 4) Binance 가격 레벨에 맞춰 수량 매핑
    out_bids = []
    for bin_price, _ in bin_bids:
        qty = 0.0
        for my_price, my_qty in my_bids.items():
            if abs(my_price - bin_price) <= PRICE_TOLERANCE:
                qty += my_qty
        out_bids.append([bin_price, qty])

    out_asks = []
    for bin_price, _ in bin_asks:
        qty = 0.0
        for my_price, my_qty in my_asks.items():
            if abs(my_price - bin_price) <= PRICE_TOLERANCE:
                qty += my_qty
        out_asks.append([bin_price, qty])

    # 5) mid price (원하면 Binance 기준으로)
    mid = None
    if bin_bids and bin_asks:
        best_bid = bin_bids[0][0]
        best_ask = bin_asks[0][0]
        mid = (best_bid + best_ask) / 2

    return {
        "bids": out_bids,
        "asks": out_asks,
        "mid": mid,
    }
