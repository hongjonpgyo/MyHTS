# api/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend_binance_old.services.ws_manager import WSManager
from backend_binance_old.services.auth_service import AuthService

router = APIRouter()
ws_manager = WSManager()

@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...)
):
    user_id = AuthService.get_user_id_from_token(token)
    if not user_id:
        await ws.close(code=1008)
        return

    await ws_manager.connect(ws, user_id)

    try:
        while True:
            data = await ws.receive_text()
            # 필요하면 클라 → 서버 메시지 처리
            print(f"[WS recv] {user_id}: {data}")

    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id)
