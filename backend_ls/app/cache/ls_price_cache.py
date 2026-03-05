# backend_ls/app/cache/ls_price_cache.py
from decimal import Decimal, ROUND_DOWN


class LSPriceCache:
    def __init__(self):
        self._by_symbol = {}      # symbol -> tick
        self._by_symbol_id = {}   # symbol_id -> tick
        self._orderbook = {}
        self._tick_size = {}

    def update_tick(self, tick):
        self._by_symbol[tick.symbol] = tick

        if hasattr(tick, "symbol_id") and tick.symbol_id:
            self._by_symbol_id[tick.symbol_id] = tick

    def get(self, symbol: str):
        return self._by_symbol.get(symbol)

    def get_by_symbol_id(self, symbol_id: int):
        return self._by_symbol_id.get(symbol_id)

    def get_all(self):
        return list(self._by_symbol.values())

    # =====================================================
    # ✅ MARKET 주문용 현재가 조회
    # =====================================================
    def get_last_price(self, symbol: str):
        """
        MARKET 주문에서 사용할 '현재가'
        """
        tick = self._by_symbol.get(symbol)
        if not tick:
            return None

        # tick 객체에 어떤 필드가 있든 여기서만 흡수
        if hasattr(tick, "last_price"):
            return float(tick.last_price)

        if hasattr(tick, "price"):
            return float(tick.price)

        if hasattr(tick, "close"):
            return float(tick.close)

        return None

    # -----------------------
    # ORDERBOOK (OVH)
    # -----------------------
    def update_orderbook(self, symbol: str, bids: list, asks: list):
        self._orderbook[symbol] = {
            "bids": bids,
            "asks": asks,
        }

    def get_orderbook(self, symbol: str):
        return self._orderbook.get(symbol)

    # =====================================================
    # 🔥 Tick Size
    # =====================================================
    def set_tick_size(self, symbol: str, tick_size: float | str | Decimal):
        print("set_tick_size : ", tick_size)
        self._tick_size[symbol] = Decimal(str(tick_size))

    def get_tick_size(self, symbol: str) -> Decimal:
        return self._tick_size.get(symbol, Decimal("1"))  # 기본 1

    def normalize_price(self, symbol: str, price: float | Decimal) -> float:
        tick_size = self.get_tick_size(symbol)

        price_d = Decimal(str(price))

        normalized = (
            (price_d / tick_size)
            .to_integral_value(rounding=ROUND_DOWN)
            * tick_size
        )

        return float(normalized)

ls_price_cache = LSPriceCache()
