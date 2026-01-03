import requests
from typing import List, Dict, Optional
from backend_ls.app.core.ls_config import LS_BASE_URL
from backend_ls.app.services.ls_auth_service import get_auth_headers

def fetch_futures_master(
    exch_cd: Optional[str] = None
) -> List[Dict]:
    """
    해외선물 마스터 조회

    exch_cd:
      - CME
      - HKEX
      - LME
      - EUREX
      - None → 전체
    """

    url = f"{LS_BASE_URL}/overseas-futureoption/market-data"

    headers = get_auth_headers("o3101")

    body = {
        "o3101InBlock": {
            "gubun": "1"
        }
    }

    r = requests.post(url, headers=headers, json=body, timeout=10)
    r.raise_for_status()
    return r.json()


