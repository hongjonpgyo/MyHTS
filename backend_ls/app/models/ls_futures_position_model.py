from sqlalchemy import Column, Integer, Numeric, String, DateTime
from backend_ls.app.db.ls_db import Base
from sqlalchemy.sql import func


class Position(Base):
    __tablename__ = "positions"

    position_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    symbol = Column(String(16), nullable=False)

    qty = Column(Numeric(18, 6), nullable=False)
    entry_price = Column(Numeric(18, 6), nullable=False)

    # 🔥 실현손익
    realized_pnl = Column(Numeric(18, 2), nullable=False, default=0)

    # 🔥 계약 승수
    multiplier = Column(Numeric(18, 6), nullable=False, default=1)

    # 🔥 계약당 개시증거금
    opng_mgn = Column(Numeric(18, 2), nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )