import asyncio
from collections import defaultdict
from typing import Dict

# symbol → asyncio.Queue
_trade_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)


def get_trade_queue(symbol: str) -> asyncio.Queue:
    return _trade_queues[symbol.upper()]


def publish_trade(symbol: str, trade: dict):
    """
    trade = {
        symbol, price, qty, side, ts
    }
    """
    queue = _trade_queues[symbol.upper()]

    # 🔥 폭주 방지 (optional, 추천)
    if queue.qsize() > 1000:
        return  # drop

    queue.put_nowait(trade)
