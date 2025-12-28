from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.services.orderbook.orderbook_service import get_orderbook

router = APIRouter(prefix="/orderbook", tags=["Orderbook"])


@router.get("/{symbol_code}/{account_id}")
def merged_orderbook(symbol_code: str, account_id: int, db: Session = Depends(get_db)):
    return get_orderbook(symbol_code, account_id, db)
