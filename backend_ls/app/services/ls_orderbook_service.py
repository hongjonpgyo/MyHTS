# backend_ls/app/services/ls_orderbook_service.py

from backend_ls.app.cache.ls_orderbook_cache import ls_orderbook_cache
from backend_ls.app.services.ls_orderbook_engine import OrderBookEngine

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderBookRow:
    price: float
    bid_qty: int = 0
    bid_cnt: int = 0
    ask_qty: int = 0
    ask_cnt: int = 0

    is_center: bool = False
    is_ls_price: bool = False

class LSOrderBookService:

    @staticmethod
    def build_from_cache(
        engine: OrderBookEngine,
        symbol: str,
        center_price: float,
        my_orders: dict | None = None,
    ):
        data = ls_orderbook_cache.get(symbol)
        if not data:
            return False

        bids = data.get("bids", [])
        asks = data.get("asks", [])

        engine.build(
            bids=bids,
            asks=asks,
            center_price=center_price,
            my_orders=my_orders or {},
        )
        engine.mark_ls_price(center_price)
        return True
