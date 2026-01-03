# backend_ls/app/cache/price_cache.py

import time
from threading import Lock

class PriceCache:
    def __init__(self):
        self._data = {}
        self._lock = Lock()

    def update(self, symbol: str, price: float, raw: dict):
        with self._lock:
            self._data[symbol] = {
                "symbol": symbol,
                "price": price,
                "raw": raw,
                "ts": time.time()
            }

    def get(self, symbol: str):
        return self._data.get(symbol)

    def get_all(self):
        return list(self._data.values())

    def clear(self):
        self._data.clear()


price_cache = PriceCache()
