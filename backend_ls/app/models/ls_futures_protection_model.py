from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    Boolean,
    func,
)
from backend_ls.app.db.ls_db import Base


class LSFuturesProtection(Base):
    __tablename__ = "protections"

    # -----------------------------
    # PK
    # -----------------------------
    id = Column(Integer, primary_key=True, autoincrement=True)

    # -----------------------------
    # 식별 정보
    # -----------------------------
    account_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)

    # -----------------------------
    # 포지션 정보
    # -----------------------------
    side = Column(String(10), nullable=False)   # LONG / SHORT
    type = Column(String(5), nullable=False)    # TP / SL

    # -----------------------------
    # 주문 정보
    # -----------------------------
    price = Column(Numeric(15, 5), nullable=False)
    qty = Column(Integer, nullable=False)

    # -----------------------------
    # 상태 관리
    # -----------------------------
    is_active = Column(Boolean, nullable=False, default=True)

    # -----------------------------
    # 타임스탬프
    # -----------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
