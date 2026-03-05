from sqlalchemy import text


class LSFuturesWatchlistRepository:

    @staticmethod
    def fetch_watchlist(db, only_has_price: bool, limit: int):
        sql = """
        SELECT *
        FROM ls_futures_watchlist_view
        """

        if only_has_price:
            sql += " WHERE last_price IS NOT NULL AND is_active = 'Y' "

        sql += " ORDER BY symbol LIMIT :limit"

        return db.execute(
            text(sql),
            {"limit": limit}
        ).mappings().all()

    # 🔥 체결용 단건 조회
    @staticmethod
    def get_by_symbol(db, symbol: str):
        sql = """
        SELECT
            symbol,
            multiplier,
            opng_mgn,
            mntnc_mgn,
            crncy_cd
        FROM ls_futures_watchlist_view
        WHERE symbol = :symbol
        """

        return db.execute(
            text(sql),
            {"symbol": symbol}
        ).mappings().first()