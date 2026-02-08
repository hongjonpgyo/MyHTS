# backend_ls/app/services/ls_orderbook_engine.py
from typing import List
from backend_ls.app.services.ls_orderbook_service import OrderBookRow


class OrderBookEngine:
    def __init__(self, depth: int, tick_size: float):
        self.depth = depth
        self.tick_size = tick_size
        self.rows: List[OrderBookRow] = []

    def clear(self):
        self.rows.clear()

    def build(self, bids: list, asks: list, center_price: float, my_orders=None):
        """
        bids / asks = [{price, qty, cnt}]
        """
        self.rows.clear()

        center_price = float(center_price)

        # 기준 가격 목록 생성
        prices = [
            round(center_price + i * self.tick_size, 2)
            for i in range(self.depth, -self.depth - 1, -1)
        ]

        price_map = {p: OrderBookRow(price=p) for p in prices}

        for a in asks:
            p = round(float(a["price"]), 2)
            if p in price_map:
                price_map[p].ask_qty = a["qty"]
                price_map[p].ask_cnt = a["cnt"]

        for b in bids:
            p = round(float(b["price"]), 2)
            if p in price_map:
                price_map[p].bid_qty = b["qty"]
                price_map[p].bid_cnt = b["cnt"]

        for p in prices:
            row = price_map[p]
            if p == round(center_price, 2):
                row.is_center = True
                row.is_ls_price = True
            self.rows.append(row)

    def mark_ls_price(self, price: float):
        p = round(price, 2)
        for r in self.rows:
            r.is_ls_price = (r.price == p)
