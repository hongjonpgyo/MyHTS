from backend.db.database import SessionLocal
from backend_ls.app.ls_api.futures_master import fetch_futures_master
from backend_ls.app.repositories.ls_future_master_repository import LSFuturesMasterRepository

def get_active_futures(db, base_code: str):
    repo = LSFuturesMasterRepository()
    active = repo.get_active_by_base(db, base_code)

    if not active:
        raise ValueError(f"No active contract for {base_code}")

    return active


def sync_ls_futures_master():
    response = fetch_futures_master()
    rows = response["o3101OutBlock"]

    db = SessionLocal()
    try:
        repo = LSFuturesMasterRepository()
        repo.upsert(db, rows)
        db.commit()
    finally:
        db.close()

    return {
        "count": len(rows),
        "status": "ok"
    }

