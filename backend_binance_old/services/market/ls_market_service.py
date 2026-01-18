# services/ls_market_service.py
import requests
from backend_binance_old.services.ls_auth_service import LSAuthService
from backend_binance_old.config.ls_settings import LS_BASE_URL, LS_APP_KEY, LS_APP_SECRET

class LSMarketService:

    @staticmethod
    def get_ls_futures_price(token: str, symbol_code: str):
        url = f"{LS_BASE_URL}/overseas-futureoption/market-data"

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "authorization": f"Bearer {token}",
            "tr_cd": "o3105",
            "tr_cont": "N",
            "tr_cont_key": "",
            "mac_address": ""
        }

        body = {
            "o3105InBlock": {
                "symbol": symbol_code
            }
        }

        r = requests.post(url, headers=headers, json=body, timeout=5)
        print(r)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_ls_futures_master(self):
        url = f"{LS_BASE_URL}/overseas-futureoption/market-data"
        token = LSAuthService.get_token()

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "tr_cd": "o3101",
            "tr_cont": "N",
            "tr_cont_key": "",
        }

        body = {
            "o3101InBlock": {
                "gubun": "1"
            }
        }

        r = requests.post(url, headers=headers, json=body, timeout=10)
        r.raise_for_status()
        return r.json()
