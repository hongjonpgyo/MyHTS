from sqlalchemy import Column, Integer, Numeric, TIMESTAMP, ForeignKey
from backend_binance_old.db.database import Base


class MarketPrice(Base):
    __tablename__ = "market_price"

    symbol_id = Column(Integer, ForeignKey("symbols.symbol_id"), primary_key=True)
    price = Column(Numeric(20, 8))
    bid = Column(Numeric(20, 8))
    ask = Column(Numeric(20, 8))
    timestamp = Column(TIMESTAMP)
