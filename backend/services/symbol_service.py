from sqlalchemy.orm import Session

from backend.config.symbol_registry import SYMBOL_REGISTRY
from backend.models.symbol_model import Symbol

def get_symbol_id(db: Session, symbol_code: str) -> int:
    row = db.query(Symbol).filter(Symbol.symbol_code == symbol_code).first()
    if not row:
        raise Exception(f"Unknown symbol: {symbol_code}")
    return row.symbol_id


def get_symbol_meta(symbol: str) -> dict:
    symbol = symbol.upper()
    if symbol not in SYMBOL_REGISTRY:
        raise ValueError(f"Unsupported symbol: {symbol}")
    return SYMBOL_REGISTRY[symbol]


def is_crypto(symbol: str) -> bool:
    return get_symbol_meta(symbol)["type"] == "crypto"


def is_futures(symbol: str) -> bool:
    return get_symbol_meta(symbol)["type"] == "futures"