from backend_ls.app.repositories.ls_futures_watchlist_repo import LSFuturesWatchlistRepository


class LSFuturesService:

    @staticmethod
    def get_watchlist(db, only_has_price: bool, limit: int):
        return LSFuturesWatchlistRepository.fetch_watchlist(
        db,
            only_has_price=only_has_price,
            limit=limit
        )

