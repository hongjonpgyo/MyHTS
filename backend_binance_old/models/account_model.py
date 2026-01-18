from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey
from backend_binance_old.db.database import Base


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    account_type = Column(String(50), default="FUTURES")
    currency = Column(String(10), default="USD")

    balance = Column(Numeric(20, 4), default=0)
    margin_used = Column(Numeric(20, 4), default=0)
    margin_available = Column(Numeric(20, 4), default=0)

    pnl_realized = Column(Numeric(20, 4), default=0)
    pnl_unrealized = Column(Numeric(20, 4), default=0)

    status = Column(String(20), default="ACTIVE")
    created_at = Column(TIMESTAMP)
