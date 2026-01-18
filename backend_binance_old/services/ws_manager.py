# services/ws_manager.py
from typing import Dict
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.users: Dict[int, WebSocket] = {}

    async def connect(self, ws: WebSocket, user_id: int):
        await ws.accept()
        self.users[user_id] = ws
        print(f"[WS] user {user_id} connected")

    async def disconnect(self, user_id: int):
        self.users.pop(user_id, None)
        print(f"[WS] user {user_id} disconnected")

    async def send_to_user(self, user_id: int, message: dict):
        ws = self.users.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for ws in self.users.values():
            await ws.send_json(message)
