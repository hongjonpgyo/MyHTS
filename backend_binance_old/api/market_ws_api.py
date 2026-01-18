from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
import asyncio

from backend_binance_old.services.market.market_service import market_service
from backend_binance_old.services.symbol_service import is_crypto

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/price/{symbol_code}")
async def price_stream(websocket: WebSocket, symbol_code: str):
    if not is_crypto(symbol_code):
        await websocket.close(code=1008)  # policy violation
        return

    await websocket.accept()
    symbol = symbol_code.upper()

    try:
        while True:
            price = market_service.get_price(symbol)
            if price:
                await websocket.send_json(price)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {symbol}")
    except Exception as e:
        print(f"[WS ERROR] {e}")
