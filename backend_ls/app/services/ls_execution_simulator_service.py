# backend_ls/app/services/ls_execution_simulator_service.py

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_order_model import Order
from backend_ls.app.models.ls_futures_execution_model import Execution
from backend_ls.app.models.ls_futures_position_model import Position
from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster


class ExecutionSimulator:
    """
    체결 시뮬레이터

    원칙:
    - on_price_tick: LIMIT 주문만 체결
    - MARKET 주문은 LSOrderService에서 _fill_order()로 즉시 체결 (틱 파이프라인 금지)
    """

    # -------------------------------------------------
    # Entry: price tick (LIMIT 전용)
    # -------------------------------------------------
    @staticmethod
    def on_price_tick(db: Session, symbol: str, last_price: float):
        price = Decimal(str(last_price))

        open_orders = (
            db.query(Order)
            .filter(
                Order.symbol == symbol,
                Order.status == "OPEN",
                Order.order_type == "LIMIT",  # ✅ 명시적으로 LIMIT만
            )
            .order_by(Order.created_at.asc())
            .all()
        )

        for order in open_orders:
            if ExecutionSimulator._is_fillable(order, price):
                ExecutionSimulator._fill_order(db, order, price)

        db.commit()

    # -------------------------------------------------
    # Fill condition (LIMIT 기준)
    # -------------------------------------------------
    @staticmethod
    def _is_fillable(order: Order, price: Decimal) -> bool:
        # ✅ 여기서 MARKET 처리 제거 (틱에서 MARKET 다루지 않음)
        if order.request_price is None:
            return True  # 안전장치

        request_price = Decimal(str(order.request_price))

        if order.side == "BUY":
            return price <= request_price
        if order.side == "SELL":
            return price >= request_price

        return False

    # -------------------------------------------------
    # Fill order (공통)
    # -------------------------------------------------
    @staticmethod
    def fill_market_order(db: Session, order: Order, last_price: float):
        """
        ✅ MARKET 전용 진입점
        - LSOrderService에서 호출
        - tick 파이프라인 사용 금지
        """
        price = Decimal(str(last_price))
        ExecutionSimulator._fill_order(db, order, price)
        db.commit()

    @staticmethod
    def _fill_order(db: Session, order: Order, price: Decimal):
        # ✅ 중복 체결 방지(결정타)
        if getattr(order, "status", None) != "OPEN":
            return

        qty = Decimal(str(order.qty))
        price = Decimal(str(price))  # 타입 안전

        # 1) Order 상태 변경
        order.status = "DONE"
        order.exec_price = price

        # 2) Execution 기록
        execution = Execution(
            order_id=order.order_id,
            account_id=order.account_id,
            symbol=order.symbol,
            side=order.side,
            price=price,
            qty=qty,
            source=order.source,
        )
        db.add(execution)
        db.flush()

        # 3) Position 반영
        ExecutionSimulator._update_position(db, order, price, qty)

        # 4) 실시간 push
        executed_at_dt = execution.created_at or datetime.now(timezone.utc)

        ExecutionBroadcaster.publish(
            exec_type="TRADE",
            account_id=order.account_id,
            symbol=order.symbol,
            side=order.side,
            price=float(price),
            qty=float(qty),
            order_id=order.order_id,
            executed_at=executed_at_dt.isoformat(),
            source=order.source,
        )

    # -------------------------------------------------
    # Position update
    # -------------------------------------------------
    @staticmethod
    def _update_position(db: Session, order: Order, price: Decimal, qty: Decimal):
        pos = (
            db.query(Position)
            .filter(
                Position.account_id == order.account_id,
                Position.symbol == order.symbol,
            )
            .one_or_none()
        )

        price = Decimal(str(price))
        qty = Decimal(str(qty))

        # BUY = +, SELL = -
        delta_qty = qty if order.side == "BUY" else -qty

        # 신규 포지션
        if not pos:
            pos = Position(
                account_id=order.account_id,
                symbol=order.symbol,
                qty=delta_qty,
                entry_price=price,
                realized_pnl=Decimal("0"),
            )
            db.add(pos)
            return

        old_qty = Decimal(str(pos.qty))
        entry_price = Decimal(str(pos.entry_price))
        new_qty = old_qty + delta_qty

        # 같은 방향 → 평균가
        if old_qty * delta_qty > 0:
            total_cost = (entry_price * abs(old_qty)) + (price * abs(delta_qty))
            pos.qty = new_qty
            pos.entry_price = total_cost / abs(new_qty)
            return

        # 부분 청산
        if abs(delta_qty) < abs(old_qty):
            realized = (price - entry_price) * abs(delta_qty)
            if old_qty < 0:
                realized *= -1
            pos.realized_pnl += realized
            pos.qty = new_qty
            return

        # 전량 청산
        if abs(delta_qty) == abs(old_qty):
            realized = (price - entry_price) * abs(old_qty)
            if old_qty < 0:
                realized *= -1
            pos.realized_pnl += realized
            pos.qty = Decimal("0")
            pos.entry_price = Decimal("0")
            return

        # 포지션 전환
        realized = (price - entry_price) * abs(old_qty)
        if old_qty < 0:
            realized *= -1
        pos.realized_pnl += realized
        pos.qty = new_qty
        pos.entry_price = price

    # -------------------------------------------------
    # Test helper
    # -------------------------------------------------
    @staticmethod
    def push_mock_price(db: Session, symbol: str, price: float):
        print(f"[MOCK PRICE] {symbol} -> {price}")
        ExecutionSimulator.on_price_tick(db=db, symbol=symbol, last_price=price)
