import asyncio
import threading
from collections import defaultdict
from typing import Optional

from .cqg import MockCQGAdapter
from .market_cache import MarketCache
from .market_stream import MarketStream
from ..symbol_service import get_symbol_meta
from ..trade_stream import publish_trade


class MarketService:

    def __init__(self):
        self.cache = MarketCache()

        self.cqg = MockCQGAdapter()
        self.cqg.set_price_handler(self._on_price)
        self.cqg.set_trade_handler(self._on_trade)

        self.stream = MarketStream(self.cache)
        self.loop = None
        self.thread = None

        self._symbols: list[str] = []

    # ==================================================
    # Symbol 관리
    # ==================================================
    def add_symbol(self, symbol: str):
        symbol = symbol.upper()
        meta = get_symbol_meta(symbol)

        if symbol not in self._symbols:
            self._symbols.append(symbol)

        # CRYPTO만 Binance WS 사용
        if meta["price_source"] == "binance":
            self.stream.add_symbol(symbol)

        print("📈 MARKET SYMBOLS:", self._symbols)

    @property
    def symbols(self):
        return self._symbols

    # ==================================================
    # Start
    # ==================================================
    def start(self):
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.stream.connect())

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

        # CQG (Mock)
        self.cqg.subscribe("NQ")
        self.cqg.subscribe("MNQ")
        self.cqg.start()

        print("🚀 MarketService started.")

    # ==================================================
    # Price access
    # ==================================================
    def get_price(self, symbol: str) -> Optional[dict]:
        return self.cache.get(symbol)

    def get_all_symbols(self):
        return self.cache.get_all_symbols()

    def get_cache(self, symbol: str):
        return self.cache.get(symbol)

    # ==================================================
    # Event handlers
    # ==================================================
    def _on_price(self, data: dict):
        self.cache.update(
            data["symbol"],
            data.get("bid"),
            data.get("ask"),
            data.get("last"),
        )

    def _on_trade(self, data: dict):
        publish_trade(data["symbol"], data)

    # ==================================================
    # Tick / Orderbook Logic (🔥 핵심)
    # ==================================================
    def quantize_price(self, price: float, tick: float) -> float:
        return round(round(price / tick) * tick, 8)

    def build_tick_grid(self, mid: float, tick: float, depth: int):
        return [
            self.quantize_price(mid + i * tick, tick)
            for i in range(depth, -depth - 1, -1)
        ]

    def build_orderbook_from_cache(
        self,
        symbol: str,
        depth: int = 100,
    ):
        cache = self.cache.get(symbol)
        if not cache:
            return None

        meta = get_symbol_meta(symbol)
        tick = meta["tick"]

        bid = cache.get("bid")
        ask = cache.get("ask")

        if bid is None or ask is None:
            return None

        # 1️⃣ mid tick 고정
        mid_raw = (bid + ask) / 2
        mid = self.quantize_price(mid_raw, tick)

        # 2️⃣ tick grid
        grid = self.build_tick_grid(mid, tick, depth)

        # 3️⃣ raw depth
        raw_bids = cache.get("depth_bids", [])
        raw_asks = cache.get("depth_asks", [])

        # 4️⃣ tick 기준 집계
        agg_bid = defaultdict(lambda: {"qty": 0.0, "count": 0})
        agg_ask = defaultdict(lambda: {"qty": 0.0, "count": 0})

        for p, q in raw_bids:
            p = self.quantize_price(p, tick)
            agg_bid[p]["qty"] += float(q)
            agg_bid[p]["count"] += 1

        for p, q in raw_asks:
            p = self.quantize_price(p, tick)
            agg_ask[p]["qty"] += float(q)
            agg_ask[p]["count"] += 1

        asks = []
        bids = []

        for price in grid:
            if price > mid:
                row = agg_ask.get(price, {"qty": 0, "count": 0})
                asks.append({
                    "price": price,
                    "db_all_qty": row["qty"],
                    "db_all_count": row["count"],
                })
            elif price < mid:
                row = agg_bid.get(price, {"qty": 0, "count": 0})
                bids.append({
                    "price": price,
                    "db_all_qty": row["qty"],
                    "db_all_count": row["count"],
                })

        return {
            "symbol": symbol,
            "mid": mid,
            "tick": tick,
            "asks": asks,
            "bids": bids,
        }


market_service = MarketService()
