# repositories/favorite_repository.py
from sqlalchemy.orm import Session
from backend.models.favorite_model import FavoriteSymbol

class FavoriteRepository:

    def get_by_user(self, db: Session, user_id: int):
        return (
            db.query(FavoriteSymbol)
            .filter(FavoriteSymbol.user_id == user_id)
            .order_by(FavoriteSymbol.sort_order, FavoriteSymbol.id)
            .all()
        )

    def get_one(self, db: Session, user_id: int, symbol_code: str):
        return (
            db.query(FavoriteSymbol)
            .filter(
                FavoriteSymbol.user_id == user_id,
                FavoriteSymbol.symbol_code == symbol_code
            )
            .first()
        )

    def create(self, db: Session, user_id: int, symbol_code: str):
        favorite = FavoriteSymbol(
            user_id=user_id,
            symbol_code=symbol_code
        )
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite

    def delete(self, db: Session, user_id: int, symbol_code: str):
        favorite = self.get_one(db, user_id, symbol_code)
        if not favorite:
            return False

        db.delete(favorite)
        db.commit()
        return True
