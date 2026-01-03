from backend_ls.app.repositories.ls_futures_master_raw_repo import (
    LSFuturesMasterRawRepository
)

class LSFuturesMasterRawService:

    @staticmethod
    def upsert_from_0310(db, outblocks: list[dict]):
        rows = [
            map_0310_outblock_to_row(b)
            for b in outblocks
        ]
        LSFuturesMasterRawRepository.upsert(db, rows)


