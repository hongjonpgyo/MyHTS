# backend_ls/app/services/ls_execution_simulator_service.py

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_order_model import Order
from backend_ls.app.models.ls_futures_execution_model import Execution
from backend_ls.app.models.ls_futures_position_model import Position
from backend_ls.app.models.ls_futures_account_balance_model import LSAccountBalance
from backend_ls.app.models.ls_futures_protection_model import LSFuturesProtection
from backend_ls.app.realtime.balance_broadcast import BalanceBroadcaster
from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster
from backend_ls.app.repositories.ls_futures_master_repo import master_repo
from backend_ls.app.repositories.ls_futures_watchlist_repo import LSFuturesWatchlistRepository
from backend_ls.app.services.account.account_snapshot_service import AccountSnapshotService


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

        ExecutionSimulator._deactivate_protections(
            db=db,
            account_id=order.account_id,
            symbol=order.symbol,
        )

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

        db.commit()

        snapshot = AccountSnapshotService.calculate(db, order.account_id)

        BalanceBroadcaster.publish(
            account_id=order.account_id,
            data=snapshot
        )

    @staticmethod
    def _deactivate_protections(db: Session, account_id: int, symbol: str):
        db.query(LSFuturesProtection).filter(
            LSFuturesProtection.account_id == account_id,
            LSFuturesProtection.symbol == symbol,
            LSFuturesProtection.is_active == True,
        ).update(
            {"is_active": False},
            synchronize_session=False,
        )

    # -------------------------------------------------
    # Position update
    # -------------------------------------------------
    @staticmethod
    def _update_position(db: Session, order: Order, price: Decimal, qty: Decimal):

        price = Decimal(str(price))
        qty = Decimal(str(qty))

        delta_qty = qty if order.side == "BUY" else -qty

        # 기존 포지션 조회
        pos = (
            db.query(Position)
            .filter(
                Position.account_id == order.account_id,
                Position.symbol == order.symbol,
            )
            .one_or_none()
        )

        # 마스터 정보 조회 (multiplier / 증거금)
        row = LSFuturesWatchlistRepository.get_by_symbol(db, order.symbol)
        if not row:
            raise Exception(f"Master not found for {order.symbol}")

        multiplier = Decimal(str(row["multiplier"]))
        opng_mgn = Decimal(str(row["opng_mgn"]))

        # -------------------------------------------------
        # 1️⃣ 신규 포지션
        # -------------------------------------------------
        if not pos:
            db.add(Position(
                account_id=order.account_id,
                symbol=order.symbol,
                qty=delta_qty,
                entry_price=price,
                realized_pnl=Decimal("0"),
                multiplier=multiplier,
                opng_mgn=opng_mgn,
            ))
            db.flush()
            return

        if pos and Decimal(str(pos.qty)) == 0:
            pos.qty = delta_qty
            pos.entry_price = price
            pos.realized_pnl = Decimal("0")
            pos.multiplier = multiplier
            pos.opng_mgn = opng_mgn
            db.flush()
            return

        old_qty = Decimal(str(pos.qty))
        old_entry = Decimal(str(pos.entry_price))
        realized = Decimal(str(pos.realized_pnl or 0))

        new_qty = old_qty + delta_qty

        # -------------------------------------------------
        # 2️⃣ 같은 방향 (추가 진입)
        # -------------------------------------------------
        if old_qty * delta_qty > 0:
            total_cost = (
                    old_entry * abs(old_qty)
                    + price * abs(delta_qty)
            )

            pos.qty = new_qty
            pos.entry_price = total_cost / abs(new_qty)

            return

        # -------------------------------------------------
        # 3️⃣ 반대 방향 (청산 포함)
        # -------------------------------------------------
        close_qty = min(abs(old_qty), abs(delta_qty))
        direction = Decimal("1") if old_qty > 0 else Decimal("-1")

        realized_pnl = (
                (price - old_entry)
                * close_qty
                * multiplier
                * direction
        )

        # 🔥 계좌 잔고에 즉시 반영
        account = (
            db.query(LSAccountBalance)
            .filter(LSAccountBalance.account_id == order.account_id)
            .one()
        )

        account.balance = Decimal(str(account.balance)) + realized_pnl

        realized += realized_pnl

        # -------------------------------------------------
        # 4️⃣ 완전 청산
        # -------------------------------------------------
        if new_qty == 0:
            pos.qty = Decimal("0")
            pos.entry_price = Decimal("0")
            pos.realized_pnl = Decimal("0")  # 이미 계좌에 반영했으므로 초기화
            return

        # -------------------------------------------------
        # 5️⃣ 포지션 전환 (롱 → 숏 or 반대)
        # -------------------------------------------------
        if old_qty * new_qty < 0:
            pos.qty = new_qty
            pos.entry_price = price  # 🔥 새 방향은 체결가가 평단
            pos.realized_pnl = Decimal("0")
            return

        # -------------------------------------------------
        # 6️⃣ 부분 청산 (방향 유지)
        # -------------------------------------------------
        pos.qty = new_qty
        pos.realized_pnl = realized

    # -------------------------------------------------
    # Test helper
    # -------------------------------------------------
    @staticmethod
    def push_mock_price(db: Session, symbol: str, price: float):
        print(f"[MOCK PRICE] {symbol} -> {price}")
        ExecutionSimulator.on_price_tick(db=db, symbol=symbol, last_price=price)
