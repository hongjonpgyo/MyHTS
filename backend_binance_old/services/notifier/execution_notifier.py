# backend_binance_old/services/notifier/execution_notifier.py
import asyncio
import json

class ExecutionNotifier:
    def __init__(self):
        # account_id → set(websocket)
        self.connections = {}

    async def connect(self, websocket, account_id: int):
        await websocket.accept()
        self.connections.setdefault(account_id, set()).add(websocket)

    def disconnect(self, websocket, account_id: int):
        conns = self.connections.get(account_id)
        if conns and websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, account_id: int, execution: dict):
        """특정 계좌에 실시간 체결 정보 push"""
        if account_id not in self.connections:
            return

        msg = json.dumps(execution)
        dead = []

        for ws in self.connections[account_id]:
            try:
                await ws.send_text(msg)
            except:
                dead.append(ws)

        # 실패한 소켓 제거
        for ws in dead:
            self.connections[account_id].remove(ws)


execution_notifier = ExecutionNotifier()
