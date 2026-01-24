from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend_ls.app.db.ls_db import Base


class OrderReservation(Base):
    __tablename__ = "order_reservations"

    reservation_id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)

    # 주문 방향 (실제 주문 side)
    side = Column(String(10), nullable=False)              # BUY / SELL
    qty = Column(Numeric(20, 4), nullable=False)

    # 트리거 조건
    trigger_op = Column(String(2), nullable=False)         # >= / <=
    trigger_price = Column(Numeric(20, 8), nullable=False)

    # 트리거 후 생성될 주문
    order_type = Column(String(10), nullable=False)        # LIMIT / MARKET
    request_price = Column(Numeric(20, 8), nullable=True)

    # 상태
    status = Column(
        String(20),
        nullable=False,
        default="WAITING",
        index=True,
    )

    # 🔥 핵심 연결
    linked_position_id = Column(Integer, nullable=True)
    protection_id = Column(
        Integer,
        nullable=True,
        index=True,
        # ForeignKey("ls_futures_protections.id")  # FK 걸어도 되고
    )

    # 시간
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
