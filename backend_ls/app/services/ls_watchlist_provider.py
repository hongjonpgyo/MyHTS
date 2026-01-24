from typing import List

from sqlalchemy.orm import Session

from backend_ls.app.models.ls_watchlist import LSWatchlistRow
from backend_ls.app.config.symbols import LSSYMBOLS

class WatchlistProvider:
    def get_rows(self):
        raise NotImplementedError

class ConfigWatchlistProvider(WatchlistProvider):
    async def get_rows(self) -> List[LSWatchlistRow]:
        # async 형태 유지 (중요!)
        rows = []
        for s in LSSYMBOLS:
            rows.append(
                LSWatchlistRow(
                    symbol=s.symbol,
                    name=s.name,
                    last_price=None,
                    change=None,
                )
            )
        return rows

class DBWatchlistProvider(WatchlistProvider):
    def __init__(self, db: Session):
        self.db = db
    async def get_rows(self):
        return None