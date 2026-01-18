# backend_ls/app/models/ls_futures_account_balance_model.py

from sqlalchemy import Column, Integer, Numeric, String, DateTime
from backend_ls.app.db.ls_db import Base

class LSAccountBalance(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True)

    user_id = Column(Integer)
    account_type = Column(String(50))
    currency = Column(String(10))

    balance = Column(Numeric(20, 4))           # 예탁금
    margin_used = Column(Numeric(20, 4))       # 사용 증거금
    margin_available = Column(Numeric(20, 4))  # 가용 예탁금

    pnl_realized = Column(Numeric(20, 4))      # 실현 손익
    pnl_unrealized = Column(Numeric(20, 4))    # 평가 손익

    status = Column(String(20))
    created_at = Column(DateTime)
