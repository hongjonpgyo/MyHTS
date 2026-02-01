# backend_ls/app/routers/ls_futures_router.py
import asyncio
import json
from datetime import datetime
from types import SimpleNamespace

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_protection_model import LSFuturesProtection
from backend_ls.app.models.ls_reservation_model import OrderReservation
from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster
from backend_ls.app.realtime.price_broadcast import PriceBroadcaster
from backend_ls.app.repositories.ls_futures_protection_repo import protection_repo
from backend_ls.app.repositories.ls_futures_reservation_repo import reservation_repo
from backend_ls.app.schemas.ls_order_schema import OrderCreate, OrderCancelRequest
from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.db.ls_db import get_db
from backend_ls.app.ls_api.tr_0167 import call_t0167
from backend_ls.app.models.ls_futures_login_model import LoginResponse, LoginRequest, SignupRequest, FindIdRequest, PasswordResetRequest, \
    PasswordResetConfirm
from backend_ls.app.schemas.ls_account_schema import AccountBalanceOut
from backend_ls.app.schemas.ls_order_schema import OrderResponse
from backend_ls.app.schemas.ls_position_schema import PositionOut, ClosePositionResponse, ClosePositionRequest
from backend_ls.app.schemas.ls_protection_schema import ProtectionCreate, ProtectionCancelRequest
from backend_ls.app.schemas.ls_reservation_schema import ReservationOut, ReservationCreate
from backend_ls.app.services.ls_execution_service import LSExecutionService, ls_execution_service
from backend_ls.app.services.fx_service import FXService
from backend_ls.app.services.ls_account_service import LSAccountService
from backend_ls.app.services.ls_watchlist_factory import get_watchlist_provider
from backend_ls.app.services.ls_watchlist_provider import ConfigWatchlistProvider
from backend_ls.app.services.ls_futures_service import LSFuturesService
from backend_ls.app.services.ls_order_service import LSOrderService
from backend_ls.app.services.ls_position_service import LSPositionService
from backend_ls.app.services.ls_rollover_service import LSRolloverService
from backend_ls.app.services.ls_auth_service import ls_auth_service
from backend_ls.app.services.ls_favorite_service import ls_favorite_service
from backend_ls.app.repositories.ls_futures_user_repo import user_repo
from backend_ls.app.utils.ls_password_util import hash_password
from backend_ls.app.schemas.ls_favorite_schema import FavoriteCreate, FavoriteOut
from backend_ls.app.core import ls_realtime_manager
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/ls/futures", tags=["LS FUTURES"])

class OrderBookSymbolRequest(BaseModel):
    symbol: str

@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 🔹 JSON body 로 들어온 값 사용
    user, token, account_id = ls_auth_service.login(
        db, payload.email, payload.password
    )

    return LoginResponse(
        access_token=token,
        user_id=user.user_id,
        account_id=account_id,
    )

@router.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(400, "비밀번호는 6자 이상")

    if user_repo.get_by_email(db, req.email):
        raise HTTPException(400, "이미 존재하는 이메일")

    password_hash = hash_password(req.password)

    user_repo.create(
        db=db,
        email=req.email,
        password_hash=password_hash,
    )

    return {"ok": True}

@router.post("/find-id")
def find_id(payload: FindIdRequest, db: Session = Depends(get_db)):
    print(payload.email)
    user = user_repo.get_by_email(db, payload.email)
    if not user:
        raise HTTPException(404, "User not found")

    return {"email": user.email}

@router.post("/password/reset/request")
def request_password_reset(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    ls_auth_service.request_password_reset(db, payload.email)
    return {"ok": True}

@router.post("/password/reset/confirm")
def reset_confirm(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    ls_auth_service.reset_password(
        db, payload.token, payload.new_password
    )
    return {"ok": True}

# -------------------------------------------------
# Futures Master / Watchlist
# -------------------------------------------------
@router.get("/active/{base_code}")
def get_active_futures(base_code: str, db: Session = Depends(get_db)):
    return LSRolloverService.get_active_with_rollover(db, base_code)


@router.get("/watchlist")
async def get_watchlist(
    only_has_price: bool = False,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    provider = get_watchlist_provider(db)
    return await provider.get_rows()
    # return LSFuturesService.get_watchlist(
    #     db,
    #     only_has_price=only_has_price,
    #     limit=limit,
    # )

@router.get("/config/watchlist")
def get_config_watchlist():
    return ConfigWatchlistProvider.get_rows()

# -------------------------------------------------
# Price
# -------------------------------------------------
@router.get("/price/{symbol}")
def get_price(symbol: str):
    tick = ls_price_cache.get(symbol)
    if not tick:
        raise HTTPException(404, "price not found")
    return tick


@router.get("/price")
def get_all_prices():
    return ls_price_cache.get_all()


@router.get("/quote/{symbol}")
def get_ls_quote(symbol: str):
    tick = ls_price_cache.get(symbol)
    if not tick:
        raise HTTPException(404, "price not found")

    return {
        "symbol": tick.symbol,
        "price": tick.price,
        "change": tick.change,
        "change_rate": tick.change_rate,
        "time": tick.trade_time,
        "source": tick.source,
    }


# -------------------------------------------------
# Time
# -------------------------------------------------
@router.get("/time")
def get_ls_time():
    out = call_t0167()
    return {
        "ls_date": out.get("dt"),
        "ls_time": out.get("time"),
        "ls_datetime": f"{out.get('dt')} {out.get('time')}",
    }


# -------------------------------------------------
# Orders
# -------------------------------------------------
@router.post("/orders", response_model=OrderResponse)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    print("🔥 ORDER PAYLOAD:", payload.dict())
    order = LSOrderService.create_order(db, payload)
    db.commit()
    return order

@router.get("/orders/open")
def get_open_orders(
    account_id: int,
    db: Session = Depends(get_db),
):
    return LSOrderService.get_open_orders(db, account_id)

# -------------------------------------------------
# Orders Cancel
# -------------------------------------------------
@router.post("/orders/cancel_orders")
def cancel_orders(
    payload: OrderCancelRequest,
    db: Session = Depends(get_db),
):
    try:
        order = LSOrderService.cancel_orders(db, payload.order_ids)
        db.commit()
        return order
    except Exception:
        db.rollback()
        raise


# -------------------------------------------------
# Positions
# -------------------------------------------------
@router.get("/accounts/{account_id}/positions", response_model=list[PositionOut])
def get_positions(account_id: str, db: Session = Depends(get_db)):
    return LSPositionService.get_positions(db, account_id)


@router.get("/accounts/{account_id}/positions/{symbol}", response_model=PositionOut | None)
def get_position(account_id: str, symbol: str, db: Session = Depends(get_db)):
    return LSPositionService.get_position(db, account_id, symbol)

@router.get(
    "/accounts/{account_id}/balance",
    response_model=AccountBalanceOut
)
def get_account_balance(
    account_id: int,
    db: Session = Depends(get_db),
):
    row = LSAccountService.get_balance(db, account_id)
    if not row:
        raise HTTPException(404, "account balance not found")

    deposit = float(row.balance or 0)
    available = float(row.margin_available or 0)
    unrealized = float(row.pnl_unrealized or 0)

    rate = (unrealized / deposit * 100) if deposit != 0 else 0.0

    return AccountBalanceOut(
        account_id=row.account_id,
        deposit=deposit,
        available=available,
        unrealized_pnl=unrealized,
        unrealized_pnl_rate=rate,
    )


@router.get("/favorites", response_model=list[FavoriteOut])
def get_favorites(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.replace("Bearer ", "")
    user_id = ls_auth_service.get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return ls_favorite_service.list(db, user_id)



@router.post("/favorites", response_model=FavoriteOut)
def add_favorite(
    data: FavoriteCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.replace("Bearer ", "")
    user_id = ls_auth_service.get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    fav = ls_favorite_service.add(db, user_id, data.symbol_code)
    if not fav:
        raise HTTPException(status_code=409, detail="Already exists")

    return fav



@router.delete("/favorites/{symbol_code}")
def delete_favorite(
    symbol_code: str,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.replace("Bearer ", "")
    user_id = ls_auth_service.get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    ok = ls_favorite_service.remove(db, user_id, symbol_code)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")

    return {"ok": True}

@router.get("/execution/stream")
async def stream_executions(request: Request):
    """
    체결현황 실시간 스트림

    - 모든 체결 이벤트를 push
    - 내 체결 / 시장 체결 구분 없음
    - UI / WS / polling 공용
    """
    q = ExecutionBroadcaster.subscribe()

    async def event_generator():
        try:
            while True:
                # 클라이언트 연결 끊기면 종료
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(q.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    # keep-alive (프록시 / 브라우저 대응)
                    yield ":\n\n"
                    continue

                # SSE 형식
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        finally:
            ExecutionBroadcaster.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

@router.get("/executions/my/{account_id}")
def executions_my(
    account_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    token = authorization.replace("Bearer ", "")
    user_id = ls_auth_service.get_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return ls_execution_service.get_my_executions(db, user_id, account_id)


@router.post("/reservation", response_model=ReservationOut)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
):
    # -------------------------
    # 기본 유효성
    # -------------------------
    if payload.qty <= 0:
        raise HTTPException(400, "qty must be > 0")

    if payload.order_type == "LIMIT" and payload.request_price is None:
        raise HTTPException(400, "LIMIT 예약은 request_price 필요")

    # -------------------------
    # 예약 생성
    # -------------------------
    row = OrderReservation(
        account_id=payload.account_id,
        symbol=payload.symbol,

        side=payload.side,
        qty=payload.qty,

        trigger_op=payload.trigger_op,
        trigger_price=payload.trigger_price,

        order_type=payload.order_type,
        request_price=payload.request_price,

        linked_position_id=payload.linked_position_id,
        status="WAITING",
    )

    return reservation_repo.create(db, row)

@router.get("/reservation", response_model=list[ReservationOut])
def list_reservations(
    account_id: int,
    db: Session = Depends(get_db),
):
    return reservation_repo.list_by_account(db, account_id)

@router.post("/reservation/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    row = reservation_repo.cancel(db, reservation_id)
    if not row:
        raise HTTPException(404, "reservation not found")

    return row

# @router.post("/mock/price")
# def mock_price(symbol: str, price: float, db: Session = Depends(get_db)):
#     # 1️⃣ fake tick 생성
#     tick = SimpleNamespace(
#         symbol=symbol,
#         price=price,
#         change=0,
#         change_rate=0,
#         trade_time=datetime.now().strftime("%H%M%S"),
#         source="MOCK",
#     )
#
#     # 2️⃣ 가격 캐시 갱신 (🔥 핵심)
#     ls_price_cache.update_tick(tick)
#
#     # 3️⃣ 트리거 / 체결 시뮬레이터 호출 (🔥 핵심)
#     ExecutionSimulator.on_price_tick(
#         db=db,
#         symbol=symbol,
#         last_price=price,
#     )
#
#     return {
#         "ok": True,
#         "symbol": symbol,
#         "price": price,
#     }
#
# @router.post("/execution/test")
# def test_execution():
#     from datetime import datetime
#     from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster
#
#     ExecutionBroadcaster.publish(
#         symbol="HSIF26",
#         side="BUY",
#         price=26950.0,
#         qty=1,
#         executed_at=datetime.now(),
#         account_id=1,
#         order_id=999,
#     )
#
#     return {"ok": True}

@router.post("/protections", response_model=dict)
def create_protections(
    payload: ProtectionCreate,
    db: Session = Depends(get_db),
):
    print("🔥 PROTECTION PAYLOAD:", payload.dict())

    rows = LSFuturesService.create_protections(
        db=db,
        payload=payload,
    )

    return {
        "ok": True,
        "count": len(rows),
        "items": [
            {
                "protection_id": r.id,
                "account_id": r.account_id,
                "symbol": r.symbol,
                "side": r.side,
                "type": r.type,
                "price": float(r.price),
                "qty": r.qty,
                "status": "WAITING",
                "source": payload.source,
            }
            for r in rows
        ],
    }

@router.get("/protections")
def get_protections(
    account_id: int,
    symbol: str | None = None,
    db: Session = Depends(get_db),
):
    return LSFuturesService.get_protections(
        db,
        account_id=account_id,
        symbol=symbol,
    )

@router.post("/protections/cancel")
def cancel_protections(
    payload: ProtectionCancelRequest,
    db: Session = Depends(get_db),
):
    try:
        LSFuturesService.cancel_protections(
            db,
            account_id=payload.account_id,
            symbol=payload.symbol,
        )
        db.commit()
        return {"ok": True}
    except Exception:
        db.rollback()
        raise

@router.post("/close_all")
def close_all(
    symbol: str,
    account_id: int,
    db: Session = Depends(get_db),
):
    try:
        # ---------------------------------
        # 0️⃣ 현재 포지션 조회
        # ---------------------------------
        pos = LSPositionService.get_position(
            db=db,
            account_id=account_id,
            symbol=symbol,
        )

        if not pos:
            raise HTTPException(409, "청산할 포지션이 없습니다.")

        position_qty = abs(int(pos["qty"]))
        if position_qty <= 0:
            raise HTTPException(409, "청산 수량이 0입니다.")

        # 포지션 반대 방향으로 청산
        close_side = "SELL" if pos["side"] == "LONG" else "BUY"

        # ---------------------------------
        # 1️⃣ 예약 주문 취소
        # ---------------------------------
        reservation_repo.cancel_waiting_by_symbol(
            db=db,
            account_id=account_id,
            symbol=symbol,
        )

        # ---------------------------------
        # 2️⃣ 보호주문 비활성화
        # ---------------------------------
        protection_repo.deactivate_by_symbol(
            db=db,
            account_id=account_id,
            symbol=symbol,
        )

        # ---------------------------------
        # 3️⃣ 시장가 청산 주문
        # ---------------------------------
        LSOrderService.create_order(
            db=db,
            payload=OrderCreate(
                account_id=account_id,
                symbol=symbol,
                side=close_side,
                order_type="MARKET",
                qty=position_qty,
                source="SYSTEM",
            ),
        )

        # ---------------------------------
        # 4️⃣ 단일 커밋
        # ---------------------------------
        db.commit()

        return {
            "ok": True,
            "symbol": symbol,
            "closed_qty": position_qty,
            "side": close_side,
        }

    except Exception:
        db.rollback()
        raise

@router.get("/price/stream")
async def stream_prices(request: Request):
    q = PriceBroadcaster.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(q.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    yield ":\n\n"
                    continue

                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        finally:
            PriceBroadcaster.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
@router.post("/orderbook/symbol")
def set_orderbook_symbol(req: OrderBookSymbolRequest):
    if not ls_realtime_manager.ls_ws_client:
        raise HTTPException(500, "LS WS not initialized")
    print("~~~~~orderbook symbol change start~~~~~~~~~")
    print(req.symbol)
    ls_realtime_manager.ls_ws_client.set_ovc_symbol(req.symbol)
    return {"ok": True, "symbol": req.symbol}

@router.get("/fx/rates")
def get_fx_rates():
    return FXService.get_all()




