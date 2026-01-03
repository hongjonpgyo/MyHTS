from backend_ls.app.db.database import SessionLocal
from backend_ls.app.ls_api.futures_master import fetch_futures_master
from backend_ls.app.repositories.ls_futures_symbol_repository import LSFuturesSymbolRepository

def sync_ls_futures_symbols():
    result = fetch_futures_master()
    rows = result.get("o3101OutBlock", [])

    db = SessionLocal()
    try:
        repo = LSFuturesSymbolRepository()
        repo.upsert_futures_master(db, rows)
        db.commit()
    finally:
        db.close()

    return {
        "count": len(rows),
        "status": "ok"
    }

