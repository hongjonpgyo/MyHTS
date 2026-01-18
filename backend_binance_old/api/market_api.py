from fastapi import APIRouter
from backend_binance_old.services.market.market_service import market_service

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/price/{symbol_code}")
def get_price(symbol_code: str):
    price = market_service.get_price(symbol_code.upper())
    if not price:
        return {"error": "No market data"}
    return price
