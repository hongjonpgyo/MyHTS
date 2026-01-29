from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_raw_3105 import LSFuturesRaw3105


class LSFuturesRaw3105Service:
    """
    LS 3105 TR 결과를 ls_futures_raw_3105 테이블에 UPSERT

    - PK / UNIQUE: symbol
    - 성공한 종목만 rows로 전달됨 (호출 제한 / 실패 종목은 상위에서 제외)
    - 항상 최신 스냅샷 유지 (히스토리 목적 아님)
    """

    @staticmethod
    def upsert_from_3105(db: Session, rows: list[dict]) -> int:
        if not rows:
            return 0

        count = 0

        for row in rows:
            symbol = row.get("Symbol")
            if not symbol:
                continue

            stmt = insert(LSFuturesRaw3105).values(
                symbol=symbol,
                symbol_nm=row.get("SymbolNm"),
                appl_date=row.get("ApplDate"),

                bsc_gds_cd=row.get("BscGdsCd"),
                bsc_gds_nm=row.get("BscGdsNm"),

                exch_cd=row.get("ExchCd"),
                exch_nm=row.get("ExchNm"),

                ec_cd=row.get("EcCd"),
                crncy_cd=row.get("CrncyCd"),
                nota_cd=row.get("NotaCd"),

                unt_prc=row.get("UntPrc"),
                mn_chg_amt=row.get("MnChgAmt"),
                rglt_fctr=row.get("RgltFctr"),
                ctrt_pr_amt=row.get("CtrtPrAmt"),

                lstng_m_cnt=row.get("LstngMCnt"),
                gds_cd=row.get("GdsCd"),
                mrkt_cd=row.get("MrktCd"),
                emini_cd=row.get("EminiCd"),

                lstng_yr=row.get("LstngYr"),
                lstng_m=row.get("LstngM"),
                seq_no=row.get("SeqNo"),

                lstng_dt=row.get("LstngDt"),
                mrtr_dt=row.get("MrtrDt"),
                fnl_dl_dt=row.get("FnlDlDt"),
                fst_trsf_dt=row.get("FstTrsfDt"),

                ec_prc=row.get("EcPrc"),

                di_dt=row.get("DiDt"),
                di_str_tm=row.get("DiStrtTm"),
                di_end_tm=row.get("DiEndTm"),

                ovs_str_day=row.get("OvsStrDay"),
                ovs_str_tm=row.get("OvsStrTm"),
                ovs_end_day=row.get("OvsEndDay"),
                ovs_end_tm=row.get("OvsEndTm"),

                di_psbl_cd=row.get("DiPsblCd"),
                mgn_clt_cd=row.get("MgnCltCd"),

                opng_mgn=row.get("OpngMgn"),
                mntnc_mgn=row.get("MntncMgn"),
                opng_mgn_r=row.get("OpngMgnR"),
                mntnc_mgn_r=row.get("MntncMgnR"),

                dot_gb=row.get("DotGb"),
                time_diff=row.get("TimeDiff"),

                ovs_date=row.get("OvsDate"),
                kor_date=row.get("KorDate"),
                trd_tm=row.get("TrdTm"),
                rcv_tm=row.get("RcvTm"),

                trd_p=row.get("TrdP"),
                trd_q=row.get("TrdQ"),
                tot_q=row.get("TotQ"),
                trd_amt=row.get("TrdAmt"),
                tot_amt=row.get("TotAmt"),

                open_p=row.get("OpenP"),
                high_p=row.get("HighP"),
                low_p=row.get("LowP"),
                close_p=row.get("CloseP"),

                ydiff_p=row.get("YdiffP"),
                ydiff_sign=row.get("YdiffSign"),
                cgbun=row.get("Cgbun"),
                diff=row.get("Diff"),
            )

            # symbol 충돌 시 최신 값으로 갱신
            stmt = stmt.on_conflict_do_update(
                index_elements=["symbol"],
                set_={
                    col.name: getattr(stmt.excluded, col.name)
                    for col in LSFuturesRaw3105.__table__.columns
                    if col.name not in ("symbol", "created_at")
                },
            )

            db.execute(stmt)
            count += 1

        db.commit()
        return count
