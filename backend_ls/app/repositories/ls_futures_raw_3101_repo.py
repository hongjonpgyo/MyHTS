from sqlalchemy.dialects.postgresql import insert
from backend_ls.app.models.ls_futures_raw_3101 import LSFuturesRaw3101


class LSFuturesRaw3101Repository:

    @staticmethod
    def upsert(db, rows: list[dict]):
        if not rows:
            return

        stmt = insert(LSFuturesRaw3101).values(rows)

        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in LSFuturesRaw3101.__table__.columns
            if c.name not in ("symbol", "created_at")
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol"],
            set_=update_cols
        )

        db.execute(stmt)
        db.commit()
