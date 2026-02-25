from collections import defaultdict
import asyncio
import json


class BalanceBroadcaster:

    _subscribers = defaultdict(list)

    @classmethod
    async def subscribe(cls, account_id: int):
        queue = asyncio.Queue()
        cls._subscribers[account_id].append(queue)
        return queue

    @classmethod
    def unsubscribe(cls, account_id: int, queue):
        cls._subscribers[account_id].remove(queue)

    @classmethod
    def publish(cls, account_id: int, data: dict):
        if account_id not in cls._subscribers:
            return

        payload = json.dumps(data)

        for queue in cls._subscribers[account_id]:
            queue.put_nowait(payload)