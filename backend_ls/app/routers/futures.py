from fastapi import APIRouter, HTTPException

from backend_ls.app.cache.price_cache import price_cache
from backend_ls.app.db.database import get_db
from backend_ls.app.services.ls_futures_master_service import sync_ls_futures_master
from backend_ls.app.services.ls_futures_symbols_service import sync_ls_futures_symbols
from fastapi import Depends
from sqlalchemy.orm import Session
from backend_ls.app.services.ls_rollover_service import LSRolloverService

router = APIRouter(prefix="/ls/futures", tags=["LS FUTURES"])

@router.post("/symbols/sync")
def sync_symbols():
    return sync_ls_futures_symbols()

@router.post("/master/sync")
def sync_master():
    return sync_ls_futures_master()

@router.get("/active/{base_code}")
def get_active_futures(
    base_code: str,
    db: Session = Depends(get_db)   # ✅ 주입
):
    return LSRolloverService.get_active_with_rollover(db, base_code)

@router.get("/price/{symbol}")
def get_price(symbol: str):
    data = price_cache.get(symbol)
    if not data:
        raise HTTPException(404, "price not found")
    return data

@router.get("/price")
def get_all_prices():
    return price_cache.get_all()
