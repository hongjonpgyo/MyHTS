from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.trade_stream import get_trade_queue

router = APIRouter()


@router.websocket("/ws/trades/{symbol}")
async def trades_ws(websocket: WebSocket, symbol: str):
    symbol = symbol.upper()
    await websocket.accept()

    print(f"[TRADES WS] Connected: {symbol}")

    queue = get_trade_queue(symbol)

    try:
        while True:
            trade = await queue.get()          # 🔥 여기서 대기
            await websocket.send_json(trade)   # 🔥 handler 내부 send
    except WebSocketDisconnect:
        print(f"[TRADES WS] Disconnected: {symbol}")
