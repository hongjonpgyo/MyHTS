from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP
from backend_binance_old.db.database import Base


class Symbol(Base):
    __tablename__ = "symbols"

    symbol_id = Column(Integer, primary_key=True, index=True)
    symbol_code = Column(String(50), unique=True, nullable=False)
    exchange = Column(String(50), nullable=False)

    tick_size = Column(Numeric(20, 8), nullable=False)
    tick_value = Column(Numeric(20, 8), nullable=False)
    multiplier = Column(Numeric(20, 8), nullable=False)

    initial_margin = Column(Numeric(20, 4))
    maintenance_margin = Column(Numeric(20, 4))
    expiration_date = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP)
