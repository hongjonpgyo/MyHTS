import asyncio
from typing import Dict, Any, List


class PriceBroadcaster:
    """
    시세 전용 Broadcaster
    - 현재가 변동 시 push
    - WatchList / 호가 / 차트용
    """

    _subscribers: List[asyncio.Queue] = []

    @classmethod
    def subscribe(cls) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=1000)
        cls._subscribers.append(q)
        return q

    @classmethod
    def unsubscribe(cls, q: asyncio.Queue):
        if q in cls._subscribers:
            cls._subscribers.remove(q)

    @classmethod
    def publish(
        cls,
        *,
        symbol: str,
        price: float,
        diff: float | None = None,
        source: str | None = None,
    ):
        event: Dict[str, Any] = {
            "symbol": symbol,
            "price": float(price),
            "diff": diff,
            "event_type": "PRICE",
            "source": source,
        }

        for q in list(cls._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass
