from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey
from backend_binance_old.db.database import Base


class LiquidationEvent(Base):
    __tablename__ = "liquidation_events"

    liq_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    symbol_id = Column(Integer, ForeignKey("symbols.symbol_id"))

    qty_closed = Column(Numeric(20, 4))
    price = Column(Numeric(20, 8))

    reason = Column(String(50))
    created_at = Column(TIMESTAMP)
