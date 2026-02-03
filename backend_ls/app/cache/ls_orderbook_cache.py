# backend_ls/app/cache/ls_orderbook_cache.py

import threading
from typing import Dict, List

class LSOrderBookCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._data: Dict[str, dict] = {}

    def update(self, symbol: str, bids: List[dict], asks: List[dict]):
        with self._lock:
            self._data[symbol] = {
                "bids": bids,
                "asks": asks,
            }

    def get(self, symbol: str) -> dict | None:
        with self._lock:
            return self._data.get(symbol)

    def clear(self, symbol: str):
        with self._lock:
            self._data.pop(symbol, None)


# 🔥 싱글톤
ls_orderbook_cache = LSOrderBookCache()
