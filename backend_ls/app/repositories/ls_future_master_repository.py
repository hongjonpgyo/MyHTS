from backend_ls.app.models.ls_futures_master import LSFuturesMaster
from datetime import date

MONTH_ORDER = {
    "F": 1, "G": 2, "H": 3, "J": 4,
    "K": 5, "M": 6, "N": 7, "Q": 8,
    "U": 9, "V": 10, "X": 11, "Z": 12
}

class LSFuturesMasterRepository:

    def get_active_by_base(self, db, base_code: str):
        today = date.today()
        year = today.year
        month = today.month

        rows = (
            db.query(LSFuturesMaster)
            .filter(
                LSFuturesMaster.base_code == base_code,
                LSFuturesMaster.tradable == "1"
            )
            .all()
        )

        # Python에서 월물 정렬 (안전)
        rows = [
            r for r in rows
            if (r.listing_year > year)
               or (r.listing_year == year and MONTH_ORDER[r.listing_month] >= month)
        ]

        rows.sort(
            key=lambda r: (r.listing_year, MONTH_ORDER[r.listing_month])
        )

        return rows[0] if rows else None

    def get_next_contract(self, db, base_code: str, active_symbol: str):
        return (
            db.query(LSFuturesMaster)
              .filter(
                  LSFuturesMaster.base_code == base_code,
                  LSFuturesMaster.symbol > active_symbol
              )
              .order_by(LSFuturesMaster.symbol.asc())
              .first()
        )

    @staticmethod
    def get_all_by_base(db, base_code: str):
        return (
            db.query(LSFuturesMaster)
            .filter(LSFuturesMaster.base_code == base_code)
            .filter(LSFuturesMaster.expiry_date.isnot(None))
            .all()
        )

    def get_by_symbol(self, db, symbol: str):
        return db.query(LSFuturesMaster)\
                 .filter(LSFuturesMaster.symbol == symbol)\
                 .first()

    def upsert(self, db, rows: list[dict]):
        for r in rows:
            obj = self.get_by_symbol(db, r["Symbol"])

            data = {
                "symbol": r["Symbol"],
                "symbol_name": r["SymbolNm"],
                "base_code": r["BscGdsCd"],
                "base_name": r["BscGdsNm"],
                "exchange_code": r["ExchCd"],
                "exchange_name": r["ExchNm"],
                "currency": r["CrncyCd"],
                "unit_price": r["UntPrc"],
                "min_change": r["MnChgAmt"],
                "contract_price": r["CtrtPrAmt"],
                "decimal_places": r["DotGb"],
                "listing_year": int(r["LstngYr"]),
                "listing_month": r["LstngM"],
                "expiry_price": r["EcPrc"],
                "trade_start_time": r["DlStrtTm"],
                "trade_end_time": r["DlEndTm"],
                "tradable": r["DlPsblCd"],
                "open_margin": r["OpngMgn"],
                "maintenance_margin": r["MntncMgn"],
            }

            if obj:
                for k, v in data.items():
                    setattr(obj, k, v)
            else:
                db.add(LSFuturesMaster(**data))
