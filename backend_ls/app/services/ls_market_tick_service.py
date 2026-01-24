from sqlalchemy.orm import Session

from backend_ls.app.services.ls_reservation_trigger_service import (
    LSReservationTriggerService,
)
from backend_ls.app.services.ls_execution_simulator_service import (
    ExecutionSimulator,
)

class LSMarketTickService:
    """
    시장 틱 처리 오케스트레이터
    """

    @staticmethod
    def on_tick(db: Session, symbol: str, last_price: float):
        # 1️⃣ 예약 트리거
        triggered = LSReservationTriggerService.on_tick(
            db=db,
            symbol=symbol,
            price=last_price,
        )

        if triggered:
            print(f"[RESERVATION TRIGGERED] {symbol} @ {last_price} ({triggered}건)")

        # 2️⃣ 체결 시뮬레이터
        ExecutionSimulator.on_price_tick(
            db=db,
            symbol=symbol,
            last_price=last_price,
        )
