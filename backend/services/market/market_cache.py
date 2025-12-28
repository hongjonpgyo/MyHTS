import threading
from typing import Dict, Optional, List, Tuple


class MarketCache:
    """
    심볼별 현재 시세 캐시 (thread-safe)
    - bid/ask/last + depth_bids/depth_asks 저장
    """

    def __init__(self):
        self._data: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def upsert_price(
        self,
        symbol: str,
        bid: float | None = None,
        ask: float | None = None,
        last: float | None = None,
    ):
        sym = symbol.upper()
        with self._lock:
            cur = self._data.get(sym, {})

            # 기존값 유지하면서 들어온 것만 갱신
            if bid is not None:
                cur["bid"] = float(bid)
            if ask is not None:
                cur["ask"] = float(ask)
            if last is not None:
                cur["last"] = float(last)

            # 최소 보정: last 없으면 bid/ask로 만들고, bid/ask 없으면 last로 채움
            b = cur.get("bid")
            a = cur.get("ask")
            l = cur.get("last")

            if l is None and b is not None and a is not None:
                cur["last"] = (float(b) + float(a)) / 2.0
            elif l is not None:
                if b is None:
                    cur["bid"] = float(l)
                if a is None:
                    cur["ask"] = float(l)

            self._data[sym] = cur

    def update_depth(
        self,
        symbol: str,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
    ):
        sym = symbol.upper()
        with self._lock:
            cur = self._data.get(sym, {})
            cur["depth_bids"] = bids
            cur["depth_asks"] = asks

            # best bid/ask가 있으면 같이 price도 upsert
            if bids:
                cur["bid"] = float(bids[0][0])
            if asks:
                cur["ask"] = float(asks[0][0])

            b = cur.get("bid")
            a = cur.get("ask")
            if b is not None and a is not None:
                cur["last"] = (float(b) + float(a)) / 2.0

            self._data[sym] = cur

    # 하위호환: 기존 코드가 update(symbol, bid, ask, last) 쓰는 경우
    def update(self, symbol: str, bid: float, ask: float, last: float):
        self.upsert_price(symbol, bid=bid, ask=ask, last=last)

    def get(self, symbol: str) -> Optional[dict]:
        with self._lock:
            return self._data.get(symbol.upper())

    def get_all_symbols(self):
        with self._lock:
            return list(self._data.keys())
