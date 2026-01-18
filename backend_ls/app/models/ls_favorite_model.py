# models/favorite_symbol.py
from sqlalchemy import Column, Integer, String, UniqueConstraint
from backend_binance_old.db.database import Base

class FavoriteSymbol(Base):
    __tablename__ = "favorite_symbols"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    symbol_code = Column(String(32), nullable=False)
    sort_order = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "symbol_code", name="uq_user_symbol"),
    )
