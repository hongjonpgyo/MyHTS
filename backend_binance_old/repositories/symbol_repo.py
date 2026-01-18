from sqlalchemy.orm import Session
from backend_binance_old.models.symbol_model import Symbol


class SymbolRepository:

    def get_by_code(self, db: Session, symbol_code: str):
        return db.query(Symbol).filter(Symbol.symbol_code == symbol_code).first()

    def get_by_id(self, db: Session, symbol_id: int):
        return db.query(Symbol).filter(Symbol.symbol_id == symbol_id).first()

    def get_all(self, db: Session):
        return db.query(Symbol).all()

    def create(self, db: Session, symbol_data):
        symbol = Symbol(**symbol_data.dict())
        db.add(symbol)
        db.commit()
        db.refresh(symbol)
        return symbol
