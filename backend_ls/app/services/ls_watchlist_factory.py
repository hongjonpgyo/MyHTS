from backend_ls.app.config.symbols import WATCHLIST_SOURCE
from backend_ls.app.services.ls_watchlist_provider import ConfigWatchlistProvider, DBWatchlistProvider


def get_watchlist_provider(db):
    if WATCHLIST_SOURCE == "config":
        return ConfigWatchlistProvider()
    return DBWatchlistProvider(db)
