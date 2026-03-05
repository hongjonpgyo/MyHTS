# backend_ls/app/services/ls_order_service.py
import time
from decimal import Decimal

from fastapi import HTTPException

from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.models.ls_futures_execution_model import Execution
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
        if last_price is None:
            raise HTTPException(409, "시세 미수신 상태")

        # 1️⃣ OPEN 상태로 먼저 생성
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
        db.commit()  # 🔥 반드시 commit → 미체결 조회 가능

        # 🔥 (선택) OPEN 이벤트 push
        ExecutionBroadcaster.publish(
            exec_type="ORDER",
            account_id=order.account_id,
            symbol=order.symbol,
            side=order.side,
            price=float(last_price),
            qty=float(order.qty),
            order_id=order.order_id,
            executed_at=None,
            source=order.source,
        )

        # 2️⃣ 실제 체결 (DONE 처리)
        ExecutionSimulator.fill_market_order(
            db=db,
            order=order,
            last_price=last_price,
        )

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
                "price": float(o.request_price) if o.request_price is not None else None,
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

        db.commit()  # 🔥 반드시 필요

        return {
            "ok": True,
            "canceled": [o.order_id for o in orders]
        }