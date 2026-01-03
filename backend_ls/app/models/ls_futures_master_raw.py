from sqlalchemy import (
    Column, String, Numeric, Integer, CHAR, TIMESTAMP
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class LSFuturesMasterRaw(Base):
    __tablename__ = "ls_futures_master_raw"

    symbol = Column(String(20), primary_key=True)
    symbol_nm = Column(String(50), nullable=False)
    appl_date = Column(CHAR(8), nullable=False)

    bsc_gds_cd = Column(String(10), nullable=False)
    bsc_gds_nm = Column(String(40), nullable=False)

    exch_cd = Column(String(10), nullable=False)
    exch_nm = Column(String(40), nullable=False)
    ec_cd = Column(CHAR(1), nullable=False)

    crncy_cd = Column(String(3), nullable=False)
    nota_cd = Column(String(3), nullable=False)
    gds_cd = Column(String(3), nullable=False)

    unt_prc = Column(Numeric(19, 9), nullable=False)
    mn_chg_amt = Column(Numeric(19, 9), nullable=False)
    rglt_fctr = Column(Numeric(19, 10), nullable=False)
    ctr_pr_amt = Column(Numeric(19, 9), nullable=False)
    ec_prc = Column(Numeric(19, 9))
    dot_gb = Column(Integer, nullable=False)

    lstng_yr = Column(CHAR(4), nullable=False)
    lstng_m = Column(CHAR(2), nullable=False)

    dl_strt_tm = Column(CHAR(6), nullable=False)
    dl_end_tm = Column(CHAR(6), nullable=False)
    dl_psbl_cd = Column(CHAR(1), nullable=False)

    mgn_clt_cd = Column(CHAR(1), nullable=False)
    opng_mgn = Column(Numeric(19, 2), nullable=False)
    mntnc_mgn = Column(Numeric(19, 2), nullable=False)
    opng_mgn_r = Column(Numeric(9, 3), nullable=False)
    mntnc_mgn_r = Column(Numeric(9, 3), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
