from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    DateTime,
    func,
)
from backend_ls.app.db.ls_db import Base


class Execution(Base):
    __tablename__ = "executions"   # ⚠ 실제 테이블명에 맞게 조정

    exec_id = Column(Integer, primary_key=True, index=True)

    # 주문 / 계좌
    order_id = Column(Integer, nullable=True)
    account_id = Column(Integer, nullable=True)

    # 체결 정보
    symbol = Column(String(20), nullable=False, comment="종목 코드 (예: HSIF26)")
    side = Column(String(10), nullable=False, comment="BUY / SELL")
    price = Column(Numeric(20, 8), nullable=False)
    qty = Column(Numeric(20, 4), nullable=False)

    # 수수료
    fee = Column(Numeric(20, 4), nullable=False, default=0)

    # 실행 타입
    exec_type = Column(
        String(20),
        nullable=False,
        default="TRADE",
        comment="TRADE / CANCEL 등"
    )

    # 발생 소스
    source = Column(
        String(20),
        nullable=False,
        default="ORDERBOOK",
        comment="ORDERBOOK / SIMULATOR"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
