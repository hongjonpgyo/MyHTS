# backend_ls/app/models/ls_futures_order_model.py

from sqlalchemy import Column, Integer, String, Numeric, DateTime
from backend_ls.app.db.ls_db import Base
from sqlalchemy.sql import func

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)

    account_id = Column(String(20), nullable=False)
    symbol = Column(String(20), nullable=False)

    side = Column(String(4), nullable=False)
    order_type = Column(String(10), nullable=False)

    qty = Column(Integer, nullable=False)
    request_price = Column(Numeric(18, 4))
    exec_price = Column(Numeric(18, 4))

    status = Column(String(10), nullable=False)
    source = Column(String(20), nullable=False)
    reason = Column(String(50))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
