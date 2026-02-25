# backend_ls/app/models/ls_futures_master_model.py

from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.sql import func
from backend_ls.app.db.ls_db import Base


class LSFuturesMaster(Base):
    __tablename__ = "ls_futures_master"

    # 종목코드 (HSIF26 등)
    symbol = Column(String(16), primary_key=True)

    # 종목명
    symbol_nm = Column(String(64))

    # 개시증거금 (3101: OpngMgn)
    opng_mgn = Column(Numeric(18, 2), nullable=False)

    # 유지증거금 (3101: MntncMgn)
    mntnc_mgn = Column(Numeric(18, 2), nullable=False)

    # 🔥 우리가 관리하는 승수
    multiplier = Column(Numeric(18, 6), nullable=False, default=1)

    # 틱 사이즈 (선택사항)
    tick_size = Column(Numeric(18, 6), nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )