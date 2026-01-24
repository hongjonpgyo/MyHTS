from sqlalchemy.orm import Session
from datetime import datetime
from backend_ls.app.models.ls_reservation_model import OrderReservation


class ReservationRepo:

    # -------------------------
    # Create
    # -------------------------
    @staticmethod
    def create(db: Session, r: OrderReservation):
        db.add(r)
        db.flush()
        db.refresh(r)
        return r

    # -------------------------
    # Query
    # -------------------------
    @staticmethod
    def list_waiting_by_symbol(db: Session, symbol: str):
        return (
            db.query(OrderReservation)
            .filter(
                OrderReservation.symbol == symbol,
                OrderReservation.status == "WAITING",
            )
            .all()
        )

    @staticmethod
    def list_by_account(db: Session, account_id: int):
        return (
            db.query(OrderReservation)
            .filter(OrderReservation.account_id == account_id)
            .order_by(OrderReservation.reservation_id.desc())
            .all()
        )

    # -------------------------
    # Cancel
    # -------------------------
    @staticmethod
    def cancel(db: Session, reservation_id: int):
        row = (
            db.query(OrderReservation)
            .filter(
                OrderReservation.reservation_id == reservation_id,
                OrderReservation.status == "WAITING",
            )
            .first()
        )
        if not row:
            return None

        row.status = "CANCELED"
        db.commit()
        return row

    # -------------------------
    # Trigger (🔒 핵심)
    # -------------------------
    @staticmethod
    def mark_triggered(db: Session, reservation_id: int) -> bool:
        """
        WAITING → TRIGGERED
        성공 시 True, 이미 처리되었으면 False
        """
        updated = (
            db.query(OrderReservation)
            .filter(
                OrderReservation.reservation_id == reservation_id,
                OrderReservation.status == "WAITING",
            )
            .update(
                {
                    "status": "TRIGGERED",
                    "triggered_at": datetime.utcnow(),
                }
            )
        )
        db.commit()
        return updated == 1

    @staticmethod
    def mark_done(db: Session, reservation_id: int):
        (
            db.query(OrderReservation)
            .filter(
                OrderReservation.reservation_id == reservation_id,
                OrderReservation.status == "TRIGGERED",
            )
            .update(
                {
                    "status": "DONE",
                }
            )
        )
        db.commit()

    # -------------------------
    # Rollback (🔥 안전장치)
    # -------------------------
    @staticmethod
    def rollback_triggered(db: Session, reservation_id: int) -> bool:
        """
        TRIGGERED → WAITING 롤백
        - 주문 생성 실패 시 사용
        """
        res = (
            db.query(OrderReservation)
            .filter(
                OrderReservation.reservation_id == reservation_id,
                OrderReservation.status == "TRIGGERED",
            )
            .first()
        )

        if not res:
            return False

        res.status = "WAITING"
        res.triggered_at = None
        db.commit()
        return True

    @staticmethod
    def cancel_waiting_by_symbol(self, db: Session, account_id: int, symbol: str) -> int:
        q = (
            db.query(OrderReservation)
            .filter(OrderReservation.account_id == account_id)
            .filter(OrderReservation.symbol == symbol)
            .filter(OrderReservation.status == "WAITING")
        )
        count = q.count()
        q.update({"status": "CANCELED"}, synchronize_session=False)
        return count

reservation_repo = ReservationRepo()

