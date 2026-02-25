from sqlalchemy import Column, String, Numeric
from backend_ls.app.db.ls_db import Base

class LSFuturesRaw3101(Base):
    __tablename__ = "ls_futures_raw_3101"

    symbol = Column(String(8), primary_key=True)
    symbol_nm = Column(String(50))
    appl_date = Column(String(8))

    bsc_gds_cd = Column(String(10))
    bsc_gds_nm = Column(String(40))

    exch_cd = Column(String(10))
    exch_nm = Column(String(40))

    crncy_cd = Column(String(3))
    nota_cd = Column(String(3))

    unt_prc = Column(Numeric(15, 9))
    mn_chg_amt = Column(Numeric(15, 9))
    rglt_fctr = Column(Numeric(15, 10))
    ctrt_pr_amt = Column(Numeric(15, 2))

    gds_cd = Column(String(3))
    lstng_yr = Column(String(4))
    lstng_m = Column(String(1))

    ec_prc = Column(Numeric(15, 9))

    dl_strt_tm = Column(String(6))
    dl_end_tm = Column(String(6))
    dl_psbl_cd = Column(String(1))

    mgn_clt_cd = Column(String(1))
    opng_mgn = Column(Numeric(15, 2))
    mntnc_mgn = Column(Numeric(15, 2))
    opng_mgn_r = Column(Numeric(7, 3))
    mntnc_mgn_r = Column(Numeric(7, 3))

    dot_gb = Column(Numeric(2, 0))
