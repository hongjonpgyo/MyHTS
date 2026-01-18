from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend_binance_old.db.database import get_db
from backend_binance_old.repositories.symbol_repo import SymbolRepository

router = APIRouter(prefix="/symbols", tags=["Symbols"])

symbol_repo = SymbolRepository()


@router.get("/")
def get_all_symbols(db: Session = Depends(get_db)):
    return symbol_repo.get_all(db)


@router.get("/{symbol_code}")
def get_symbol(symbol_code: str, db: Session = Depends(get_db)):
    return symbol_repo.get_by_code(db, symbol_code)
