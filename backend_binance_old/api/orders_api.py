from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from backend_binance_old.db.database import get_db
from backend_binance_old.schemas.order_schema import OrderCreate
from backend_binance_old.services.order_service import OrderService
from backend_binance_old.schemas.order_schema import LimitOrderRequest, OpenOrdersRequest
from backend_binance_old.models.order_model import Order
from backend_binance_old.models.symbol_model import Symbol
from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["Orders"])

order_service = OrderService()


@router.post("/market")
def place_market_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """
    시장가 매수/매도 주문 → 즉시 체결
    """
    result = order_service.place_market_order(
        db=db,
        account_id=payload.account_id,
        symbol_code=payload.symbol,
        side=payload.side,
        qty=payload.qty
    )
    return result


@router.post("/limit")
def place_limit_order(payload: LimitOrderRequest, db: Session = Depends(get_db)):
    result = order_service.place_limit_order(
        db=db,
        account_id=payload.account_id,
        symbol_code=payload.symbol,
        side=payload.side,
        qty=payload.qty,
        price=payload.price
    )
    return result

# ----------------------------
# 🔥 GET — 미체결 주문 조회 (클라이언트 요청 방식과 동일)
# ----------------------------
@router.get("/open/{account_id}")
def get_open_orders(account_id: int, db: Session = Depends(get_db)):
    return order_service.get_open_orders(db, account_id)



# =========================================================
#  단일 주문 취소
# =========================================================
@router.post("/cancel_orders")
def cancel_orders(payload: dict, db: Session = Depends(get_db)):
    order_ids = payload.get("order_ids", [])
    if not order_ids:
        raise HTTPException(400, "order_ids is required")

    order_service.cancel_orders(db, order_ids)

    return {"ok": True, "cancelled": order_ids}


# =========================================================
#  다중 주문 취소
# =========================================================
# ----------------------------
# 🔥 POST — 다중 주문 취소 (cancel_bulk)
# ----------------------------
# @router.post("/cancel_bulk")
# def cancel_bulk(payload: OrderCancelBulkRequest, db: Session = Depends(get_db)):
#     return order_service.cancel_bulk(db, payload.order_ids)





