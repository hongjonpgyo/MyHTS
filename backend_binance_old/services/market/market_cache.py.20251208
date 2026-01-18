import time
from typing import Dict, Any


class MarketCache:
    """
    심볼별 실시간 시세를 저장하는 캐시
    구조 예:
    {
        "BTCUSDT": {
            "bid": 43000.0,
            "ask": 43001.0,
            "last": 43000.5,
            "timestamp": 1700000000
        }
    }
    """
    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}

    def update(self, symbol: str, bid: float, ask: float, last: float = None):
        self.data[symbol] = {
            "bid": bid,
            "ask": ask,
            "last": last if last is not None else bid,
            "timestamp": int(time.time())
        }

    def get(self, symbol: str):
        return self.data.get(symbol)
