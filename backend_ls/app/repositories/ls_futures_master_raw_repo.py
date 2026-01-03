from sqlalchemy.dialects.postgresql import insert
from backend_ls.app.models.ls_futures_master_raw import LSFuturesMasterRaw


class LSFuturesMasterRawRepository:

    @staticmethod
    def upsert(db, rows: list[dict]):
        """
        rows: LS 0310 OutBlock dict list
        """
        if not rows:
            return

        stmt = insert(LSFuturesMasterRaw).values(rows)

        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in LSFuturesMasterRaw.__table__.columns
            if c.name not in ("symbol", "created_at")
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol"],
            set_=update_cols
        )

        db.execute(stmt)
        db.commit()

    def map_0310_outblock_to_row(block: dict) -> dict:
        return {
            "symbol": block["Symbol"],
            "symbol_nm": block["SymbolNm"],
            "appl_date": block["ApplDate"],

            "bsc_gds_cd": block["BscGdsCd"],
            "bsc_gds_nm": block["BscGdsNm"],

            "exch_cd": block["ExchCd"],
            "exch_nm": block["ExchNm"],
            "ec_cd": block["EcCd"],

            "crncy_cd": block["CrncyCd"],
            "nota_cd": block["NotaCd"],
            "gds_cd": block["GdsCd"],

            "unt_prc": block["UntPrc"],
            "mn_chg_amt": block["MnChgAmt"],
            "rglt_fctr": block["RgltFctr"],
            "ctr_pr_amt": block["CtrPrAmt"],
            "ec_prc": block.get("EcPrc"),
            "dot_gb": block["DotGb"],

            "lstng_yr": block["LstngYr"],
            "lstng_m": block["LstngM"],

            "dl_strt_tm": block["DlStrtTm"],
            "dl_end_tm": block["DlEndTm"],
            "dl_psbl_cd": block["DlPsblCd"],

            "mgn_clt_cd": block["MgnCltCd"],
            "opng_mgn": block["OpngMgn"],
            "mntnc_mgn": block["MntncMgn"],
            "opng_mgn_r": block["OpngMgnR"],
            "mntnc_mgn_r": block["MntncMgnR"],
        }
