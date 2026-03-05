from sqlalchemy import (
    Column, String, Numeric, CHAR, TIMESTAMP
)
from sqlalchemy.sql import func
from backend_ls.app.db.ls_db import Base

class LSFuturesRaw3105(Base):
    __tablename__ = "ls_futures_raw_3105"

    # -------------------------
    # PK
    # -------------------------
    symbol = Column(String(8), primary_key=True)

    # -------------------------
    # 기본 정보
    # -------------------------
    symbol_nm = Column(String(50))
    appl_date = Column(CHAR(8))

    bsc_gds_cd = Column(String(10))
    bsc_gds_nm = Column(String(40))

    exch_cd = Column(String(10))
    exch_nm = Column(String(40))

    ec_cd = Column(CHAR(1))
    crncy_cd = Column(CHAR(3))
    nota_cd = Column(CHAR(3))

    # -------------------------
    # 가격 / 계약 정보
    # -------------------------
    unt_prc = Column(Numeric(15, 9))
    mn_chg_amt = Column(Numeric(15, 9))
    rglt_fctr = Column(Numeric(15, 10))
    ctrt_pr_amt = Column(Numeric(15, 2))

    # -------------------------
    # 상품 / 시장 구분
    # -------------------------
    lstng_m_cnt = Column(Numeric(2, 0))
    gds_cd = Column(CHAR(3))
    mrkt_cd = Column(CHAR(3))
    emini_cd = Column(CHAR(1))

    lstng_yr = Column(CHAR(4))
    lstng_m = Column(CHAR(1))
    seq_no = Column(Numeric(5, 0))

    # -------------------------
    # 날짜 정보
    # -------------------------
    lstng_dt = Column(CHAR(8))
    mtrt_dt = Column(CHAR(8))
    fnl_dl_dt = Column(CHAR(8))
    fst_trsf_dt = Column(CHAR(8))

    ec_prc = Column(Numeric(15, 9))

    # -------------------------
    # 거래 시간 (한국)
    # -------------------------
    di_dt = Column(CHAR(8))
    di_str_tm = Column(CHAR(6))
    di_end_tm = Column(CHAR(6))

    # -------------------------
    # 거래 시간 (현지)
    # -------------------------
    ovs_str_day = Column(CHAR(8))
    ovs_str_tm = Column(CHAR(6))
    ovs_end_day = Column(CHAR(8))
    ovs_end_tm = Column(CHAR(6))

    # -------------------------
    # 거래 가능 / 증거금
    # -------------------------
    di_psbl_cd = Column(CHAR(1))
    mgn_clt_cd = Column(CHAR(1))

    opng_mgn = Column(Numeric(15, 2))
    mntnc_mgn = Column(Numeric(15, 2))
    opng_mgn_r = Column(Numeric(7, 3))
    mntnc_mgn_r = Column(Numeric(7, 3))

    dot_gb = Column(Numeric(2, 0))
    time_diff = Column(Numeric(5, 0))

    # -------------------------
    # 체결 / 시세
    # -------------------------
    ovs_date = Column(CHAR(8))
    kor_date = Column(CHAR(8))
    trd_tm = Column(CHAR(6))
    rcv_tm = Column(CHAR(6))

    trd_p = Column(Numeric(15, 9))
    trd_q = Column(Numeric(10, 0))
    tot_q = Column(Numeric(15, 0))
    trd_amt = Column(Numeric(15, 2))
    tot_amt = Column(Numeric(15, 2))

    open_p = Column(Numeric(15, 9))
    high_p = Column(Numeric(15, 9))
    low_p = Column(Numeric(15, 9))
    close_p = Column(Numeric(15, 9))

    ydiff_p = Column(Numeric(15, 9))
    ydiff_sign = Column(CHAR(1))
    cgbun = Column(CHAR(1))
    diff = Column(Numeric(6, 2))

    # -------------------------
    # Meta
    # -------------------------
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
