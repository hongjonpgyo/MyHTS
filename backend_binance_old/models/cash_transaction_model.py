from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey
from backend_binance_old.db.database import Base


class CashTransaction(Base):
    __tablename__ = "cash_transactions"

    txn_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))

    txn_type = Column(String(20))  # deposit / withdraw
    amount = Column(Numeric(20, 4))

    created_at = Column(TIMESTAMP)
