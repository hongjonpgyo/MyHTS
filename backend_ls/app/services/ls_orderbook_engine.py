from typing import List
from backend_ls.app.services.ls_orderbook_service import OrderBookRow


class OrderBookEngine:

    def __init__(self, depth: int, tick_size: float):
        self.depth = depth
        self.tick_size = tick_size
        self.rows: List[OrderBookRow] = []

        self.center_idx = None

    # -----------------------------
    # price <-> tick index
    # -----------------------------

    def _tick_index(self, price: float) -> int:
        return int(round(price / self.tick_size))

    def _price_from_index(self, idx: int) -> float:
        return round(idx * self.tick_size, 6)

    # -----------------------------
    # 초기 라더 생성
    # -----------------------------

    def _build_ladder(self, center_idx: int):

        price_indexes = [
            center_idx + i
            for i in range(self.depth, -self.depth - 1, -1)
        ]

        self.rows = [
            OrderBookRow(price=self._price_from_index(idx))
            for idx in price_indexes
        ]

    # -----------------------------
    # 오더북 업데이트
    # -----------------------------

    def build(self, bids: list, asks: list, center_price: float, my_orders=None):

        center_idx = self._tick_index(center_price)

        # 처음 생성
        if self.center_idx is None:
            self.center_idx = center_idx
            self._build_ladder(center_idx)

        # center 이동
        shift = center_idx - self.center_idx

        if shift != 0:

            if abs(shift) >= self.depth:
                # 크게 이동하면 전체 재생성
                self._build_ladder(center_idx)

            else:
                # 라더 이동
                if shift > 0:
                    for _ in range(shift):
                        self.rows.pop(0)
                        new_idx = self._tick_index(self.rows[-1].price) + 1
                        self.rows.append(
                            OrderBookRow(price=self._price_from_index(new_idx))
                        )

                else:
                    for _ in range(-shift):
                        self.rows.pop()
                        new_idx = self._tick_index(self.rows[0].price) - 1
                        self.rows.insert(
                            0,
                            OrderBookRow(price=self._price_from_index(new_idx))
                        )

        self.center_idx = center_idx

        # 초기화
        for r in self.rows:
            r.ask_qty = 0
            r.ask_cnt = 0
            r.bid_qty = 0
            r.bid_cnt = 0
            r.is_center = False

        # asks
        for a in asks:
            idx = self._tick_index(a["price"])
            for r in self.rows:
                if self._tick_index(r.price) == idx:
                    r.ask_qty = a["qty"]
                    r.ask_cnt = a["cnt"]
                    break

        # bids
        for b in bids:
            idx = self._tick_index(b["price"])
            for r in self.rows:
                if self._tick_index(r.price) == idx:
                    r.bid_qty = b["qty"]
                    r.bid_cnt = b["cnt"]
                    break

        # center 표시
        for r in self.rows:
            if self._tick_index(r.price) == center_idx:
                r.is_center = True

    # -----------------------------
    # 현재가 표시
    # -----------------------------

    def mark_ls_price(self, price: float):

        idx = self._tick_index(price)

        for r in self.rows:
            r.is_ls_price = (self._tick_index(r.price) == idx)