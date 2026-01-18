from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from backend_ls.app.db.ls_db import Base

class OrderReservation(Base):
    __tablename__ = "order_reservations"

    reservation_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)

    side = Column(String(10), nullable=False)
    qty = Column(Numeric(20, 4), nullable=False)

    trigger_op = Column(String(2), nullable=False)         # >= / <=
    trigger_price = Column(Numeric(20, 8), nullable=False)

    order_type = Column(String(10), nullable=False)        # LIMIT / MARKET
    request_price = Column(Numeric(20, 8), nullable=True)

    status = Column(String(20), nullable=False, default="WAITING", index=True)
    linked_position_id = Column(Integer, nullable=True)

    triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
