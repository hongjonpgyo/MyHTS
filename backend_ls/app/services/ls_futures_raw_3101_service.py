from backend_ls.app.models.ls_futures_raw_3101 import LSFuturesRaw3101

class LSFuturesRaw3101Service:

    @staticmethod
    def upsert_from_3101(db, rows: list[dict]):
        for r in rows:
            obj = LSFuturesRaw3101(
                symbol=r["Symbol"],
                symbol_nm=r["SymbolNm"],
                appl_date=r["ApplDate"],

                bsc_gds_cd=r["BscGdsCd"],
                bsc_gds_nm=r["BscGdsNm"],

                exch_cd=r["ExchCd"],
                exch_nm=r["ExchNm"],

                crncy_cd=r["CrncyCd"],
                nota_cd=r["NotaCd"],

                unt_prc=r.get("UntPrc"),
                mn_chg_amt=r.get("MnChgAmt"),
                rglt_fctr=r.get("RgltFctr"),
                crtr_pr_amt=r.get("CrtrPrAmt"),

                gds_cd=r["GdsCd"],
                lstng_yr=r["LstngYr"],
                lstng_m=r["LstngM"],

                ec_prc=r.get("EcPrc"),

                dl_strt_tm=r["DlStrtTm"],
                dl_end_tm=r["DlEndTm"],
                dl_psbl_cd=r["DlPsblCd"],

                mgn_clt_cd=r["MgnCltCd"],
                opng_mgn=r.get("OpngMgn"),
                mntnc_mgn=r.get("MntncMgn"),
                opng_mgn_r=r.get("OpngMgnR"),
                mntnc_mgn_r=r.get("MntncMgnR"),

                dot_gb=r["DotGb"],
            )

            db.merge(obj)

        db.commit()
