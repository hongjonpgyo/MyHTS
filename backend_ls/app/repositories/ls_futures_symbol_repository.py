from datetime import time
from backend_ls.app.models.ls_futures_symbol import LSFuturesSymbol


class LSFuturesSymbolRepository:

    def upsert_futures_master(self, db, rows: list[dict]):
        for s in rows:
            exists = self.get_by_symbol(db, s["Symbol"])

            values = dict(
                symbol_code=s["Symbol"],
                symbol_name=s["SymbolNm"],

                base_code=s["BscGdsCd"],
                base_name=s["BscGdsNm"],

                exchange_code=s["ExchCd"],
                exchange_name=s["ExchNm"],

                currency=s["CrncyCd"],

                listing_year=int(s["LstngYr"]),
                listing_month=s["LstngM"],

                tick_size=s["UntPrc"],
                tick_value=s["MnChgAmt"],
                contract_size=s["CtrtPrAmt"],

                decimal_places=int(s["DotGb"]),

                trading_start=self._parse_time(s["DlStrtTm"]),
                trading_end=self._parse_time(s["DlEndTm"]),

                is_tradable=(s["DlPsblCd"] == "1"),
            )

            if exists:
                for k, v in values.items():
                    setattr(exists, k, v)
            else:
                obj = LSFuturesSymbol(**values)
                db.add(obj)


    @staticmethod
    def get_by_symbol(db, symbol_code: str):
        return (
            db.query(LSFuturesSymbol)
            .filter(LSFuturesSymbol.symbol_code == symbol_code)
            .first()
        )
    @staticmethod
    def _parse_time(t: str | None):
        if not t:
            return None
        return time(
            hour=int(t[:2]),
            minute=int(t[2:4]),
            second=int(t[4:6]),
        )

