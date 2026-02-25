from sqlalchemy import text
from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_master_model import LSFuturesMaster


class LSFuturesMasterRepository:
    """
    ls_futures_master VIEW 전용 Repository
    (3101 + 3105 JOIN 결과)
    """
    def get_by_symbol(self, db: Session, symbol: str) -> LSFuturesMaster | None:
        return (
            db.query(LSFuturesMaster)
            .filter(LSFuturesMaster.symbol == symbol)
            .first()
        )

    def get_required_fields(self, db: Session, symbol: str) -> dict | None:
        row = (
            db.query(
                LSFuturesMaster.symbol,
                LSFuturesMaster.multiplier,
                LSFuturesMaster.opng_mgn,
                LSFuturesMaster.mntnc_mgn,
            )
            .filter(LSFuturesMaster.symbol == symbol)
            .first()
        )

        if not row:
            return None

        return {
            "symbol": row.symbol,
            "multiplier": row.multiplier,
            "opng_mgn": row.opng_mgn,
            "mntnc_mgn": row.mntnc_mgn,
        }
    @staticmethod
    def fetch_watchlist(
        db: Session,
        only_has_price: bool = False,
        exch_cd: str | None = None,
        limit: int = 200,
    ):
        sql = """
        SELECT
            symbol,
            symbol_nm,
            exch_cd,
            exch_nm,
            crncy_cd,
            lstng_yr,
            lstng_m,
            seq_no,
            trd_p,
            diff,
            diff,
            trd_tm,
            kor_date
        FROM ls_futures_raw_3105
        """

        conditions = []

        if only_has_price:
            conditions.append("trd_p IS NOT NULL")

        if exch_cd:
            conditions.append("exch_cd = :exch_cd")

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += """
        ORDER BY
            exch_cd,
            symbol
        LIMIT :limit
        """

        params = {
            "limit": limit,
        }

        if exch_cd:
            params["exch_cd"] = exch_cd

        return db.execute(
            text(sql),
            params,
        ).mappings().all()

master_repo = LSFuturesMasterRepository()