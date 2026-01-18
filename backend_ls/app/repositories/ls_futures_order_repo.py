# backend_ls/app/repositories/ls_order_repo.py

from sqlalchemy.orm import Session
from backend_ls.app.models.ls_futures_order_model import Order

class LSOrderRepository:

    def get_open_orders(self, db: Session, account_id: int):
        return (
            db.query(Order)
            .filter(
                Order.account_id == account_id,
                Order.status == "OPEN",
            )
            .order_by(Order.created_at.asc())
            .all()
        )

order_repo = LSOrderRepository()
