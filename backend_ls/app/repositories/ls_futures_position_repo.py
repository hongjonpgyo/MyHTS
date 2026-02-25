# repositories/position_repo.py

from sqlalchemy.orm import Session
from backend_ls.app.models.ls_futures_position_model import Position


class PositionRepo:

    @staticmethod
    def get_by_account(db: Session, account_id: int):
        return (
            db.query(Position)
            .filter(Position.account_id == account_id)
            .all()
        )

positionRepo = PositionRepo()