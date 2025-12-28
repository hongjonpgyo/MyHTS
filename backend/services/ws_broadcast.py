# backend/services/ws_broadcast.py
import asyncio
from fastapi import WebSocket
from typing import Dict, Set


class BroadcastManager:
    """
    queue job format:
    {
      "scope": "account" | "user" | "broadcast" | "trade",
      "target_id": int | str | None,
      "message": dict
    }
    """

    def __init__(self):
        self.account_connections: Dict[int, Set[WebSocket]] = {}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        self.queue: asyncio.Queue[dict] = asyncio.Queue()

    # -----------------------------
    # connect / disconnect
    # -----------------------------
    def connect_account(self, account_id: int, ws: WebSocket):
        self.account_connections.setdefault(account_id, set()).add(ws)

    def connect_user(self, user_id: int, ws: WebSocket):
        self.user_connections.setdefault(user_id, set()).add(ws)

    def disconnect_account(self, account_id: int, ws: WebSocket):
        conns = self.account_connections.get(account_id)
        if not conns:
            return
        conns.discard(ws)
        if not conns:
            self.account_connections.pop(account_id, None)

    def disconnect_user(self, user_id: int, ws: WebSocket):
        conns = self.user_connections.get(user_id)
        if not conns:
            return
        conns.discard(ws)
        if not conns:
            self.user_connections.pop(user_id, None)

    # -----------------------------
    # publish helpers
    # -----------------------------
    def publish_account(self, account_id: int, message: dict):
        self.queue.put_nowait({
            "scope": "account",
            "target_id": account_id,
            "message": message
        })

    def publish_user(self, user_id: int, message: dict):
        self.queue.put_nowait({
            "scope": "user",
            "target_id": user_id,
            "message": message
        })

    def publish_broadcast(self, message: dict):
        self.queue.put_nowait({
            "scope": "broadcast",
            "target_id": None,
            "message": message
        })

    # -----------------------------
    # worker
    # -----------------------------
    async def worker(self):
        print("[BroadcastManager] worker running")
        while True:
            job = await self.queue.get()
            try:
                scope = job.get("scope")
                target_id = job.get("target_id")
                message = job.get("message")

                if not isinstance(message, dict):
                    continue

                if scope == "account":
                    targets = list(self.account_connections.get(int(target_id), set()))

                elif scope == "user":
                    targets = list(self.user_connections.get(int(target_id), set()))

                elif scope == "broadcast":
                    targets = []
                    for s in self.account_connections.values():
                        targets.extend(list(s))
                    for s in self.user_connections.values():
                        targets.extend(list(s))

                else:
                    continue

                dead: Set[WebSocket] = set()
                for ws in targets:
                    try:
                        await ws.send_json(message)
                    except Exception:
                        print("dead exception")
                        dead.add(ws)

                # dead socket 정리
                if dead:
                    for aid, conns in list(self.account_connections.items()):
                        if conns & dead:
                            conns.difference_update(dead)
                            if not conns:
                                self.account_connections.pop(aid, None)

                    for uid, conns in list(self.user_connections.items()):
                        if conns & dead:
                            conns.difference_update(dead)
                            if not conns:
                                self.user_connections.pop(uid, None)

            finally:
                self.queue.task_done()


broadcast_manager = BroadcastManager()
