from typing import Optional

from sqlalchemy.orm import Session

from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster
from backend_ls.app.realtime.price_broadcast import PriceBroadcaster
from backend_ls.app.repositories.ls_futures_protection_repo import protection_repo
from backend_ls.app.repositories.ls_futures_reservation_repo import reservation_repo
from backend_ls.app.schemas.ls_order_schema import OrderCreate
from backend_ls.app.services.ls_order_service import LSOrderService


class LSReservationTriggerService:
    """
        ✅ 예약 트리거 서비스

        동작:
        - tick(symbol, price) 들어오면 WAITING 예약을 조회
        - trigger_op / trigger_price 조건 충족 시:
            1) reservation_repo.mark_triggered() 로 원자적 잠금(중복 방지)
            2) LSOrderService.create_order() 호출 (MARKET/LIMIT)
            3) reservation_repo.mark_done()
            4) ExecutionBroadcaster.publish(...) 로 UI 실시간 push

        중요:
        - mark_triggered()가 성공(True)한 경우에만 주문 생성
        - 실패(False)면 이미 다른 tick에서 처리된 것
        """

    @staticmethod
    def on_tick(db: Session, symbol: str, price: float) -> int:
        tick_price = float(price)
        waiting = reservation_repo.list_waiting_by_symbol(db, symbol)

        triggered_count = 0

        for r in waiting:
            if not LSReservationTriggerService._is_triggered(
                    r.trigger_op,
                    float(r.trigger_price),
                    tick_price,
            ):
                continue

            # 1️⃣ 원자적 선점
            if not reservation_repo.mark_triggered(db, r.reservation_id):
                continue

            try:
                # 2️⃣ 주문 생성만 담당
                LSReservationTriggerService._create_order_from_reservation(
                    db, r, tick_price
                )

                # 3️⃣ DONE 처리
                reservation_repo.mark_done(db, r.reservation_id)

                if r.protection_id:
                    protection_repo.deactivate_group(
                        db=db,
                        account_id=r.account_id,
                        symbol=r.symbol,
                        side=r.side,
                    )

                    canceled = reservation_repo.cancel_oco_siblings(
                        db,
                        r.protection_id,
                        r.reservation_id,
                    )

                    # 🔥 오더북 리프레시 트리거
                    if canceled > 0:
                        PriceBroadcaster.publish(
                            symbol=r.symbol,
                            price=tick_price,
                            source="OCO_REFRESH",
                        )

                triggered_count += 1

            except Exception:
                # 🔴 실패 시 원복 (선택)
                reservation_repo.rollback_triggered(db, r.reservation_id)
                raise

        return triggered_count

    # -------------------------------------------------
    @staticmethod
    def _is_triggered(op: str, trigger_price: float, last_price: float) -> bool:
        """
        op: "<=" or ">=" (필요하면 == 추가)
        """
        if op == "<=":
            return last_price <= trigger_price
        if op == ">=":
            return last_price >= trigger_price
        if op == "==":
            return last_price == trigger_price
        return False

    # -------------------------------------------------
    @staticmethod
    def _create_order_from_reservation(db: Session, r, tick_price: float):
        """
        reservation row -> OrderCreate -> LSOrderService.create_order
        """
        if r.order_type == "MARKET":
            # 시장가는 현재가로 체결
            request_price: Optional[float] = None  # schema상 optional
            order_type = "MARKET"
        else:
            request_price = float(r.request_price)
            order_type = "LIMIT"

        payload = OrderCreate(
            account_id=str(r.account_id),
            symbol=r.symbol,
            side=r.side,
            order_type=order_type,
            qty=int(r.qty),
            request_price=request_price,
            source="ORDERBOOK",  # 너 정책에 맞게 "RESERVATION"으로 바꿔도 OK
        )

        # ✅ create_order 내부에서 LIMIT/MARKET 분기
        return LSOrderService.create_order(db, payload)