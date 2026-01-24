# backend_ls/app/services/ls_order_service.py

from fastapi import HTTPException

from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.models.ls_futures_order_model import Order
from backend_ls.app.repositories.ls_futures_order_repo import order_repo
from backend_ls.app.schemas.ls_order_schema import OrderCreate
from sqlalchemy.orm import Session
from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster
from backend_ls.app.services.ls_execution_simulator_service import ExecutionSimulator



class LSOrderService:

    @staticmethod
    def create_order(db: Session, payload: OrderCreate):
        if payload.order_type == "LIMIT":
            return LSOrderService._create_limit_order(db, payload)

        if payload.order_type == "MARKET":
            return LSOrderService._create_market_order(db, payload)

        raise ValueError("Unsupported order_type")

    @staticmethod
    def _create_limit_order(db: Session, payload: OrderCreate):
        order = Order(
            account_id=payload.account_id,
            symbol=payload.symbol,
            side=payload.side,
            order_type="LIMIT",
            qty=payload.qty,
            request_price=payload.request_price,
            source=payload.source,
            status="OPEN",
        )
        db.add(order)
        db.flush()
        db.refresh(order)
        return order

    @staticmethod
    def _create_market_order(db: Session, payload: OrderCreate):
        last_price = ls_price_cache.get_last_price(payload.symbol)
        print(f"MARKET ORDER LAST PRICE : {last_price}")

        if last_price is None:
            raise HTTPException(
                status_code=409,
                detail="시세 미수신 상태에서는 시장가 주문이 불가합니다."
            )

        order = Order(
            account_id=int(payload.account_id),
            symbol=payload.symbol,
            side=payload.side,
            order_type="MARKET",
            qty=payload.qty,
            request_price=None,
            source=payload.source,
            status="OPEN",
        )

        db.add(order)
        db.flush()  # order_id 확보

        # 즉시 체결
        ExecutionSimulator.on_price_tick(
            db=db,
            symbol=payload.symbol,
            last_price=last_price,
        )

        # db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_open_orders(db, account_id: int):
        rows = order_repo.get_open_orders(db, account_id)

        return [
            {
                "order_id": o.order_id,
                "symbol": o.symbol,
                "side": o.side,
                "price": float(o.request_price),
                "qty": o.qty,
                "status": o.status,
                "created_at": o.created_at,
            }
            for o in rows
        ]

    @staticmethod
    def cancel_orders(db: Session, order_ids: list[int]):
        orders = (
            db.query(Order)
            .filter(
                Order.order_id.in_(order_ids),
                Order.status == "OPEN"
            )
            .all()
        )

        for o in orders:
            o.status = "CANCELED"
            o.reason = "USER_CANCEL"

        # db.commit()

        return {
            "ok": True,
            "canceled": [o.order_id for o in orders]
        }