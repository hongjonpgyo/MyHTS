from backend_binance_old.repositories.base_repo import BaseRepository
from backend_binance_old.models.position_model import Position
from sqlalchemy.orm import Session, joinedload


class PositionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Position)

    # def get_by_account(self, db, account_id: int):
    #     return db.query(self.model).filter(self.model.account_id == account_id).all()
    def get_by_account(self, db: Session, account_id: int):
        return (
            db.query(Position)
            .options(joinedload(Position.symbol))  # ← symbol JOIN 수행
            .filter(Position.account_id == account_id)
            .all()
        )

    def get_by_account_symbol(self, db: Session, account_id: int, symbol_id: int):
        return (
            db.query(Position)
            .filter(
                Position.account_id == account_id,
                Position.symbol_id == symbol_id
            )
            .first()
        )

    def update(self, db: Session, position: Position, **kwargs):
        for key, value in kwargs.items():
            setattr(position, key, value)
        db.commit()
        db.refresh(position)
        return position

position_repo = PositionRepository()
