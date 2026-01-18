import asyncio
from typing import Dict, List, Any
from datetime import datetime


class ExecutionBroadcaster:
    """
    Execution Broadcaster

    - 체결 이벤트를 실시간으로 push
    - 여러 subscriber(UI, WS 등) 지원
    - in-memory pub/sub (단일 프로세스 기준)
    """

    _subscribers: List[asyncio.Queue] = []

    # -------------------------------------------------
    # subscribe
    # -------------------------------------------------
    @classmethod
    def subscribe(cls) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=1000)
        cls._subscribers.append(q)
        return q

    # -------------------------------------------------
    # unsubscribe
    # -------------------------------------------------
    @classmethod
    def unsubscribe(cls, q: asyncio.Queue):
        if q in cls._subscribers:
            cls._subscribers.remove(q)

    # -------------------------------------------------
    # publish
    # -------------------------------------------------
    @classmethod
    def publish(
        cls,
        *,
        symbol: str,
        side: str,
        price: float,
        qty: float,
        executed_at: datetime | str | None,
        account_id: int | None = None,
        order_id: int | None = None,
        source: str | None = None,
        exec_type: str | None = None,
    ):
        """
        체결 이벤트 발행 (SSE / UI 공용)

        executed_at:
        - datetime -> isoformat
        - str      -> 그대로
        - None     -> None
        """

        # 🔒 executed_at 안전 변환
        if isinstance(executed_at, datetime):
            executed_at_out = executed_at.isoformat()
        elif isinstance(executed_at, str):
            executed_at_out = executed_at
        else:
            executed_at_out = None

        event: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "price": float(price),
            "qty": float(qty),
            "executed_at": executed_at_out,
            "account_id": account_id,
            "order_id": order_id,
            "source": source,
            "exec_type": exec_type,
        }

        # fan-out
        for q in list(cls._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # 느린 subscriber는 드롭 (정상 정책)
                pass
