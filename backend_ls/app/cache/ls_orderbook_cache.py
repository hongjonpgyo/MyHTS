# backend_ls/app/cache/ls_orderbook_cache.py
from datetime import datetime
from threading import Lock

class LSOrderBookCache:
    def __init__(self):
        self._data = {}
        self._lock = Lock()

    def update(self, symbol: str, bids: list, asks: list):
        with self._lock:
            self._data[symbol] = {
                "bids": bids,
                "asks": asks,
                "updated_at": datetime.utcnow(),
            }

    def get(self, symbol: str):
        return self._data.get(symbol)

    def clear(self, symbol: str | None = None):
        with self._lock:
            if symbol:
                self._data.pop(symbol, None)
            else:
                self._data.clear()


# 🔥 싱글톤
ls_orderbook_cache = LSOrderBookCache()
