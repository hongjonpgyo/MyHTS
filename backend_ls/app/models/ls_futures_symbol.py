from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Time
)
from backend_ls.app.db.ls_database import Base


class LSFuturesSymbol(Base):
    __tablename__ = "ls_futures_symbols"

    id = Column(Integer, primary_key=True)

    symbol_code = Column(String(20), unique=True, nullable=False)
    symbol_name = Column(String(100))

    base_code = Column(String(20))
    base_name = Column(String(100))

    exchange_code = Column(String(10))
    exchange_name = Column(String(50))

    currency = Column(String(10))

    listing_year = Column(Integer)
    listing_month = Column(String(1))

    tick_size = Column(Numeric(18, 9))
    tick_value = Column(Numeric(18, 9))
    contract_size = Column(Numeric(18, 2))

    decimal_places = Column(Integer)

    trading_start = Column(Time)
    trading_end = Column(Time)

    is_tradable = Column(Boolean)
