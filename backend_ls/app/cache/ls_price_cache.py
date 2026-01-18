# backend_ls/app/cache/ls_price_cache.py

class LSPriceCache:
    def __init__(self):
        self._by_symbol = {}      # symbol -> tick
        self._by_symbol_id = {}   # symbol_id -> tick

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

ls_price_cache = LSPriceCache()
