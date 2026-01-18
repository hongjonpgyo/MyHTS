from decimal import Decimal

from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_order_model import Order
from backend_ls.app.models.ls_futures_execution_model import Execution
from backend_ls.app.models.ls_futures_position_model import Position


class ExecutionSimulator:
    """
    LS 체결 시뮬레이터
    Order → Execution → Position
    """

    # -------------------------------------------------
    # Price Tick Entry
    # -------------------------------------------------
    @staticmethod
    def on_price_tick(db: Session, symbol: str, last_price: float):
        price = Decimal(str(last_price))  # 🔥 반드시 Decimal

        from backend_ls.app.services.ls_reservation_trigger_service import (
            LSReservationTriggerService,
        )

        LSReservationTriggerService.on_tick(
            db=db,
            symbol=symbol,
            price=price,  # ← Decimal로
        )

        open_orders = (
            db.query(Order)
            .filter(
                Order.symbol == symbol,
                Order.status == "OPEN"
            )
            .order_by(Order.created_at.asc())
            .all()
        )

        for order in open_orders:
            if ExecutionSimulator._is_fillable(order, price):
                ExecutionSimulator._fill_order(db, order, price)

        db.commit()

    # -------------------------------------------------
    # Fill 판단
    # -------------------------------------------------
    @staticmethod
    def _is_fillable(order: Order, price: Decimal) -> bool:
        request_price = Decimal(order.request_price)

        if order.side == "BUY":
            return price <= request_price
        if order.side == "SELL":
            return price >= request_price
        return False

    # -------------------------------------------------
    # Fill
    # -------------------------------------------------
    @staticmethod
    def _fill_order(db: Session, order: Order, price: Decimal):
        qty = Decimal(order.qty)

        # 1️⃣ Order 상태 변경
        order.status = "FILLED"
        order.exec_price = price

        # 2️⃣ Execution 기록
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

        # 3️⃣ Position 반영
        ExecutionSimulator._update_position(db, order, price, qty)

    # -------------------------------------------------
    # Position Update (최종)
    # -------------------------------------------------
    @staticmethod
    def _update_position(
        db: Session,
        order: Order,
        price: Decimal,
        qty: Decimal,
    ):
        pos = (
            db.query(Position)
            .filter(
                Position.account_id == order.account_id,
                Position.symbol == order.symbol,
            )
            .first()
        )

        delta_qty = qty if order.side == "BUY" else -qty

        # -------------------------------------------------
        # 1️⃣ 신규 포지션
        # -------------------------------------------------
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

        old_qty = Decimal(pos.qty)
        new_qty = old_qty + delta_qty
        entry_price = Decimal(pos.entry_price)

        # -------------------------------------------------
        # 2-1) 같은 방향 → 평균가 갱신
        # -------------------------------------------------
        if old_qty * delta_qty > 0:
            total_cost = (
                entry_price * abs(old_qty)
                + price * abs(delta_qty)
            )
            pos.qty = new_qty
            pos.entry_price = total_cost / abs(new_qty)
            return

        # -------------------------------------------------
        # 2-2) 반대 방향 → 부분 청산
        # -------------------------------------------------
        if abs(delta_qty) < abs(old_qty):
            realized = (price - entry_price) * abs(delta_qty)
            pos.realized_pnl += realized
            pos.qty = new_qty
            return

        # -------------------------------------------------
        # 2-3) 전량 청산
        # -------------------------------------------------
        if abs(delta_qty) == abs(old_qty):
            realized = (price - entry_price) * abs(old_qty)
            pos.realized_pnl += realized
            pos.qty = Decimal("0")
            pos.entry_price = Decimal("0")
            return

        # -------------------------------------------------
        # 2-4) 포지션 전환
        # -------------------------------------------------
        realized = (price - entry_price) * abs(old_qty)
        pos.realized_pnl += realized
        pos.qty = new_qty
        pos.entry_price = price

    @staticmethod
    def push_mock_price(db, symbol: str, price: float):
        """
        장 종료 시 테스트용 가격 강제 주입
        """
        print(f"[MOCK PRICE] {symbol} -> {price}")

        # 예약 트리거
        from backend_ls.app.services.ls_reservation_trigger_service import (
            LSReservationTriggerService,
        )

        LSReservationTriggerService.on_tick(
            db=db,
            symbol=symbol,
            price=price,
        )

        # 기존 체결 시뮬레이터 로직도 태우고 싶으면
        ExecutionSimulator.on_price_tick(
            db=db,
            symbol=symbol,
            last_price=price,
        )
