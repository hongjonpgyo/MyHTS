from sqlalchemy import text

class LSFuturesWatchlistRepository:

    @staticmethod
    def fetch_watchlist(db, only_has_price: bool, limit: int):
        sql = """
        SELECT *
        FROM ls_futures_watchlist_view
        """

        if only_has_price:
            sql += " WHERE last_price IS NOT NULL AND IS_ACTIVE = 'Y' "

        sql += " ORDER BY symbol LIMIT :limit"

        return db.execute(
            text(sql),
            {"limit": limit}
        ).mappings().all()
