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
            change_rate: float | None = None,
            source: str | None = None,
            event_type: str = "PRICE",
    ):
        event: Dict[str, Any] = {
            "symbol": symbol,
            "price": float(price),
            "diff": diff,  # 전일대비 가격
            "change_rate": change_rate,  # 등락률 %
            "event_type": event_type,
            "source": source,
        }

        for q in list(cls._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass

    @classmethod
    def publish_orderbook(
            cls,
            *,
            symbol: str,
            bids: list[dict],
            asks: list[dict],
            price: float | None = None,  # ✅ 추가
            tick_size : float | None = None,
            source: str | None = None,
    ):
        event = {
            "event_type": "ORDERBOOK",
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "price": price,  # ✅ 추가
            "tick_size": tick_size,
            "source": source,
        }

        for q in list(cls._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


