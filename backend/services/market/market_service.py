import asyncio
import threading

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

        self._symbols = []

    def add_symbol(self, symbol: str):
        meta = get_symbol_meta(symbol)

        if symbol not in self._symbols:
            self._symbols.append(symbol)

        # ✅ CRYPTO만 Binance WS에 등록
        if meta["price_source"] == "binance":
            self.stream.add_symbol(symbol)

        print("MARKET SYMBOLS:", self._symbols)

    @property
    def symbols(self):
        """MatchingEngine 이 접근할 심볼 리스트"""
        return self._symbols

    def start(self):
        """
        FastAPI startup 이벤트에서 호출되는 함수
        Binance WS를 별도 스레드에서 실행
        """
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.stream.connect())

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

        self.cqg.subscribe("NQ")
        self.cqg.subscribe("MNQ")
        self.cqg.start()

        print("🚀 MarketDataService 시작됨.")

    def get_price(self, symbol: str):
        meta = get_symbol_meta(symbol)

        if meta["price_source"] == "binance":
            return self.cache.get(symbol)

        if meta["price_source"] == "yahoo":
            # ⛳ 2번에서 구현 예정 (임시: last만 사용)
            return self.cache.get(symbol)  # 없으면 None

        raise ValueError("Unknown price source")

    def get_all_symbols(self):
        return self.cache.get_all_symbols()

    def get_cache(self, symbol: str):
        """심볼의 캐시된 시세 반환"""
        return self.cache.get(symbol)

    def _on_price(self, data: dict):
        self.cache.update(
            data["symbol"],
            data["bid"],
            data["ask"],
            data["last"],
        )

    def _on_trade(self, data: dict):
        publish_trade(data["symbol"], data)

market_service = MarketService()