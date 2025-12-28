from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.db.database import SessionLocal
from backend.repositories.account_repo import AccountRepository
from backend.repositories.position_repo import PositionRepository
from backend.services.auth_service import auth_service
from backend.services.account_service import account_service
from backend.services.market.market_service import market_service
from backend.services.ws_broadcast import broadcast_manager

router = APIRouter()

acc_repo = AccountRepository()
pos_repo = PositionRepository()


@router.websocket("/ws/account")
async def ws_account(
    websocket: WebSocket,
    token: str = Query(...),
    account_id: int = Query(...),
):
    await websocket.accept()

    # -------------------------
    # 1) token → user_id
    # -------------------------
    user_id = auth_service.get_user_id_from_token(token)
    if not user_id:
        await websocket.close(code=1008)
        return

    # -------------------------
    # 2) account 소유권 검증
    # -------------------------
    db = SessionLocal()
    try:
        account = acc_repo.get(db, account_id)
        if not account or int(account.user_id) != int(user_id):
            await websocket.close(code=1008)
            return
    finally:
        db.close()

    # -------------------------
    # 3) WS 연결 등록 (⭐ await 필수)
    # -------------------------
    broadcast_manager.connect_account(account_id, websocket)
    print(f"[WS] account connected user={user_id} account={account_id}")

    # ==================================================
    # 🔥 4) 초기 Account Snapshot 1회 PUSH (핵심)
    # ==================================================
    db = SessionLocal()
    try:
        positions = pos_repo.get_by_account(db, account_id)
        account = acc_repo.get(db, account_id)

        pos_rows = []
        for p in positions:
            price_info = market_service.get_price(p.symbol.symbol_code)
            last_price = price_info.get("last") if price_info else None

            qty = float(p.qty or 0)
            entry = float(p.entry_price or 0)
            multiplier = float(p.symbol.multiplier)

            if qty == 0 or last_price is None:
                upnl = 0.0
            elif qty > 0:
                upnl = (last_price - entry) * qty * multiplier
            else:
                upnl = (entry - last_price) * abs(qty) * multiplier

            liq = account_service.calc_liquidation_price(p, account, p.symbol)

            pos_rows.append({
                "symbol": p.symbol.symbol_code,
                "side": "LONG" if qty > 0 else "SHORT" if qty < 0 else "",
                "qty": qty,
                "entry_price": entry,
                "realized_pnl": float(p.realized_pnl or 0),
                "unrealized_pnl": upnl,
                "current_price": last_price,
                "liq_price": liq,
            })

        account_row = {
            "balance": float(account.balance),
            "margin_used": float(account.margin_used),
            "margin_available": float(account.margin_available),
            "pnl_realized": float(account.pnl_realized),
            "pnl_unrealized": float(account.pnl_unrealized),
        }

        await websocket.send_json({
            "type": "account_update",
            "positions": pos_rows,
            "account": account_row,
        })

    finally:
        db.close()

    # -------------------------
    # 5) 이후부터는 PUSH 대기
    # -------------------------
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        broadcast_manager.disconnect_account(account_id, websocket)
        print(f"[WS] account disconnected user={user_id} account={account_id}")
