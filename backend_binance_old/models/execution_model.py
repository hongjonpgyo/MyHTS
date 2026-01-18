from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, func
from backend_ls.app.db.ls_db import Base

class Execution(Base):
    __tablename__ = "executions"

    exec_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    account_id = Column(Integer, index=True, nullable=False)

    symbol = Column(String(20), index=True, nullable=False)
    side = Column(String(10), nullable=False)

    price = Column(Numeric(20, 8), nullable=False)
    qty = Column(Numeric(20, 4), nullable=False)
    fee = Column(Numeric(20, 4), default=0)

    exec_type = Column(String(20), default="TRADE")
    source = Column(String(20))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
