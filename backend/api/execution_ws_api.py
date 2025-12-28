# backend/api/execution_ws_api.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.db.database import SessionLocal
from backend.repositories.account_repo import AccountRepository
from backend.services.auth_service import auth_service  # ✅ 함수로 import
from backend.services.ws_broadcast import broadcast_manager

router = APIRouter()


@router.websocket("/ws/executions")
async def ws_executions(
    websocket: WebSocket,
    token: str = Query(...),
    account_id: int = Query(...),
):
    # ✅ 403 피하려면 accept 먼저 하고 close 코드로 끊는게 UX 좋음
    await websocket.accept()

    # 1) token -> user_id
    try:
        user_id = auth_service.get_user_id_from_token(token)
    except Exception as e:
        print("[WS executions] token decode error:", e)
        await websocket.close(code=1008)
        return

    if not user_id:
        await websocket.close(code=1008)
        return

    # 2) account_id 소유권 검증
    db = SessionLocal()
    try:
        account_repo = AccountRepository()
        account = account_repo.get(db, account_id)

        if not account or int(account.user_id) != int(user_id):
            await websocket.close(code=1008)
            return
    except Exception as e:
        print("[WS executions] account verify error:", e)
        await websocket.close(code=1011)
        return
    finally:
        db.close()

    # 3) 연결 등록
    broadcast_manager.connect_account(account_id, websocket)
    print(f"[WS] executions connected: user={user_id} account={account_id}")

    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("[WS executions] error:", e)
    finally:
        broadcast_manager.disconnect_account(account_id, websocket)
        print(f"[WS] executions disconnected: user={user_id} account={account_id}")
