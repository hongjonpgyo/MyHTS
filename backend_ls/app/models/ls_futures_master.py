from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date
from sqlalchemy.sql import func
from backend_ls.app.db.database import Base

class LSFuturesMaster(Base):
    __tablename__ = "ls_futures_master"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)

    symbol_name = Column(String(100))
    base_code = Column(String(20))
    base_name = Column(String(100))

    exchange_code = Column(String(20))
    exchange_name = Column(String(50))

    currency = Column(String(10))

    unit_price = Column(Numeric(18, 8))
    min_change = Column(Numeric(18, 8))
    contract_price = Column(Numeric(18, 2))
    decimal_places = Column(Integer)

    listing_year = Column(Integer)
    listing_month = Column(String(1))

    expiry_price = Column(Numeric(18, 8))

    trade_start_time = Column(String(6))
    trade_end_time = Column(String(6))
    tradable = Column(String(1))

    open_margin = Column(Numeric(18, 2))
    maintenance_margin = Column(Numeric(18, 2))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    expiry_date = Column(Date)

