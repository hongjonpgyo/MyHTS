from sqlalchemy import Column, Integer, Numeric, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend_binance_old.db.database import Base


class Position(Base):
    __tablename__ = "positions"

    position_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    symbol_id = Column(Integer, ForeignKey("symbols.symbol_id"))

    qty = Column(Numeric(20, 4), default=0)
    entry_price = Column(Numeric(20, 8))
    realized_pnl = Column(Numeric(20, 4), default=0)
    updated_at = Column(TIMESTAMP)

    # ⭐ 추가해야 하는 부분
    symbol = relationship("Symbol", lazy="joined")
    account = relationship("Account", lazy="joined")

    __table_args__ = (
        UniqueConstraint("account_id", "symbol_id"),
    )
