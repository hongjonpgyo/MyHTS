# api/routes/ls_market.py
from fastapi import APIRouter, HTTPException
from backend.services.market.ls_market_service import LSMarketService
from backend.services.ls_auth_service import LSAuthService

router = APIRouter(prefix="/ls/market", tags=["LS Market"])

@router.get("/futures/{symbol_code}")
def get_ls_futures_price(symbol_code: str):
    token = LSAuthService.get_token()
    return LSMarketService.get_ls_futures_price(token, symbol_code)

@router.get("/ls/master/futures")
def fetch_ls_futures_master():
    token = LSAuthService.get_token()
    data = LSMarketService.get_ls_futures_master(token)

    print(data)

    return data["o3101OutBlock"]