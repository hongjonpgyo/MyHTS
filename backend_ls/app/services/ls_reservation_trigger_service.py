from typing import Optional

from sqlalchemy.orm import Session

from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster
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
        """
        tick 1번 들어올 때 처리된 예약 건수 리턴
        """
        tick_price = float(price)
        waiting = reservation_repo.list_waiting_by_symbol(db, symbol)

        triggered_count = 0

        for r in waiting:
            if not LSReservationTriggerService._is_triggered(r.trigger_op, float(r.trigger_price), tick_price):
                continue

            # ✅ 원자적으로 WAITING → TRIGGERED (중복 방지)
            ok = reservation_repo.mark_triggered(db, r.reservation_id)
            if not ok:
                continue  # 이미 다른 워커/틱에서 처리

            # ✅ 주문 생성
            created_order = LSReservationTriggerService._create_order_from_reservation(db, r, tick_price)

            # ✅ DONE 처리
            reservation_repo.mark_done(db, r.reservation_id)

            # ✅ 체결 이벤트 push (UI 체결현황)
            # - 시장 체결/내 체결 구분은 account_id로 가능
            ExecutionBroadcaster.publish(
                symbol=created_order.symbol,
                side=created_order.side,
                price=float(created_order.request_price or tick_price),
                qty=float(created_order.qty),
                executed_at=created_order.created_at,  # datetime OK
                account_id=created_order.account_id,
                order_id=created_order.order_id,
                source="RESERVATION",
                exec_type="TRADE",
            )

            # ExecutionBroadcaster.publish(
            #     source="RESERVATION",
            #     exec_type="STATUS",
            #     reservation_id=r.reservation_id,
            #     status="DONE",
            #     symbol=r.symbol,
            # )

            triggered_count += 1

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

    # @staticmethod
    # def on_price_tick(
    #     db: Session,
    #     symbol: str,
    #     last_price: float,
    # ):
    #     """
    #     가격 틱 발생 시 호출
    #     """
    #     reservations = reservation_repo.get_waiting_by_symbol(
    #         db, symbol
    #     )
    #
    #     for r in reservations:
    #         if not LSReservationTriggerService._match(r, last_price):
    #             continue
    #
    #         # 🔒 선점 (중복 방지)
    #         if not reservation_repo.mark_triggered(db, r.reservation_id):
    #             continue
    #
    #         # 실제 주문 생성
    #         LSReservationTriggerService._execute(db, r)

    # @staticmethod
    # def _match(r, price: float) -> bool:
    #     if r.side == "BUY":
    #         return price <= r.trigger_price
    #     else:
    #         return price >= r.trigger_price

    # @staticmethod
    # def _execute(db: Session, r):
    #     order_payload = {
    #         "account_id": r.account_id,
    #         "symbol": r.symbol,
    #         "side": r.side,
    #         "order_type": r.order_type,
    #         "qty": r.qty,
    #         "request_price": r.request_price,
    #         "source": "RESERVATION",
    #     }
    #
    #     LSOrderService.create_order(db, order_payload)
    #
    #     reservation_repo.mark_done(db, r.reservation_id)
