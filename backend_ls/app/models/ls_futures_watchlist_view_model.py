from sqlalchemy import Column, String, Numeric, Integer
from backend_ls.app.db.ls_db import Base


class LSFuturesWatchlistView(Base):
    __tablename__ = "ls_futures_watchlist_view"
    __table_args__ = {"extend_existing": True}

    symbol = Column(String(8), primary_key=True)

    symbol_nm = Column(String(50))
    exch_nm = Column(String(40))
    crncy_cd = Column(String(3))

    last_price = Column(Numeric(15, 9))
    diff = Column(Numeric(6, 2))
    ydiff_p = Column(Numeric(15, 9))

    open_p = Column(Numeric(15, 9))
    high_p = Column(Numeric(15, 9))
    low_p = Column(Numeric(15, 9))
    close_p = Column(Numeric(15, 9))

    tick_value = Column(Numeric(15, 9))

    opng_mgn = Column(Numeric(15, 2))
    mntnc_mgn = Column(Numeric(15, 2))
    multiplier = Column(Numeric(15, 2))

    remain_days = Column(Integer)
    is_active = Column(String(1))