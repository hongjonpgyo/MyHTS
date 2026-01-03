import requests
from backend_ls.app.core.config import LS_BASE_URL
from backend_ls.app.ls_api.auth import get_access_token


def fetch_futures_price(symbol: str):
    token = get_access_token()

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "tr_cd": "o3105",
        "tr_cont": "N",
        "tr_cont_key": ""
    }

    body = {
        "o3105InBlock": {
            "symbol": symbol
        }
    }

    r = requests.post(
        f"{LS_BASE_URL}/overseas-futureoption/market-data",
        headers=headers,
        json=body,
        timeout=5
    )

    print(r.json)
    r.raise_for_status()
    return r.json()
