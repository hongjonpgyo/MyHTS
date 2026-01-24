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
    체결 시뮬레이터 (최종)

    역할:
    - OPEN 주문을 가격 기준으로 체결
    - Execution 생성
    - Position 갱신
    - ExecutionBroadcaster로 TRADE 이벤트 push

    ✅ 원칙:
    - 예약 트리거(LSReservationTriggerService)는 여기서 호출하지 않음
    """

    # -------------------------------------------------
    # Entry: price tick
    # -------------------------------------------------
    @staticmethod
    def on_price_tick(db: Session, symbol: str, last_price: float):
        """
        가격 틱 진입점
        """
        price = Decimal(str(last_price))

        open_orders = (
            db.query(Order)
            .filter(
                Order.symbol == symbol,
                Order.status == "OPEN",
            )
            .order_by(Order.created_at.asc())
            .all()
        )

        for order in open_orders:
            if ExecutionSimulator._is_fillable(order, price):
                ExecutionSimulator._fill_order(db, order, price)

        db.commit()

    # -------------------------------------------------
    # Fill condition
    # -------------------------------------------------
    @staticmethod
    def _is_fillable(order: Order, price: Decimal) -> bool:
        """
        체결 가능 여부 판단
        """
        # MARKET 주문은 즉시 체결
        if getattr(order, "order_type", None) == "MARKET":
            return True

        # 안전장치: request_price 없으면 MARKET처럼 처리
        if order.request_price is None:
            return True

        request_price = Decimal(str(order.request_price))

        if order.side == "BUY":
            return price <= request_price
        if order.side == "SELL":
            return price >= request_price

        return False

    # -------------------------------------------------
    # Fill order
    # -------------------------------------------------
    @staticmethod
    def _fill_order(db: Session, order: Order, price: Decimal):
        qty = Decimal(str(order.qty))

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
        db.flush()  # execution_id 확보 + (일부 DB에서) created_at 반영 시도

        # 3) Position 반영
        ExecutionSimulator._update_position(db, order, price, qty)

        # 4) 실시간 UI push (created_at 방어)
        executed_at_dt = execution.created_at
        if executed_at_dt is None:
            executed_at_dt = datetime.now(timezone.utc)

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
    def _update_position(
        db: Session,
        order: Order,
        price: Decimal,
        qty: Decimal,
    ):
        """
        포지션 갱신 로직 (정석)
        """
        pos = (
            db.query(Position)
            .filter(
                Position.account_id == order.account_id,
                Position.symbol == order.symbol,
            )
            .one_or_none()
        )

        # BUY = +, SELL = -
        delta_qty = qty if order.side == "BUY" else -qty

        # 1) 신규 포지션
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
        new_qty = old_qty + delta_qty
        entry_price = Decimal(str(pos.entry_price))

        # 2) 같은 방향 → 평균가
        if old_qty * delta_qty > 0:
            total_cost = (entry_price * abs(old_qty)) + (price * abs(delta_qty))
            pos.qty = new_qty
            pos.entry_price = total_cost / abs(new_qty)
            return

        # 3) 부분 청산
        if abs(delta_qty) < abs(old_qty):
            realized = (price - entry_price) * abs(delta_qty)
            if old_qty < 0:  # 기존이 SELL 포지션이면 부호 반전
                realized *= -1
            pos.realized_pnl += realized
            pos.qty = new_qty
            return

        # 4) 전량 청산
        if abs(delta_qty) == abs(old_qty):
            realized = (price - entry_price) * abs(old_qty)
            if old_qty < 0:
                realized *= -1
            pos.realized_pnl += realized
            pos.qty = Decimal("0")
            pos.entry_price = Decimal("0")
            return

        # 5) 포지션 전환
        realized = (price - entry_price) * abs(old_qty)
        if old_qty < 0:
            realized *= -1
        pos.realized_pnl += realized
        pos.qty = new_qty
        pos.entry_price = price

    # -------------------------------------------------
    # Test helper (시뮬레이터만 태움)
    # -------------------------------------------------
    @staticmethod
    def push_mock_price(db: Session, symbol: str, price: float):
        print(f"[MOCK PRICE] {symbol} -> {price}")
        ExecutionSimulator.on_price_tick(db=db, symbol=symbol, last_price=price)
