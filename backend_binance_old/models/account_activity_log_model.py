from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from backend_binance_old.db.database import Base


class AccountActivityLog(Base):
    __tablename__ = "account_activity_log"

    log_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))

    event_type = Column(String(50))
    details = Column(JSONB)

    created_at = Column(TIMESTAMP)
