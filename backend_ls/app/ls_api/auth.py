import time
import requests
from backend_ls.app.core.config import LS_APP_KEY, LS_APP_SECRET, LS_BASE_URL

_TOKEN_CACHE = {
    "access_token": None,
    "expires_at": 0
}


def _request_token() -> dict:
    url = f"{LS_BASE_URL}/oauth2/token"

    data = {
        "grant_type": "client_credentials",
        "appkey": LS_APP_KEY,
        "appsecretkey": LS_APP_SECRET,
        "scope": "oob",
    }

    r = requests.post(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def get_access_token(force: bool = False) -> str:
    """
    LS OpenAPI access token 반환
    """
    now = int(time.time())

    # 캐시된 토큰 사용
    if (
        not force
        and _TOKEN_CACHE["access_token"]
        and _TOKEN_CACHE["expires_at"] > now
    ):
        return _TOKEN_CACHE["access_token"]

    # 신규 발급
    token_data = _request_token()

    access_token = token_data["access_token"]
    expires_in = int(token_data.get("expires_in", 3600))

    _TOKEN_CACHE["access_token"] = access_token
    _TOKEN_CACHE["expires_at"] = now + expires_in - 30  # 안전 마진

    return access_token

def get_auth_headers(tr_cd: str) -> dict:
    token = get_access_token()

    return {
        # "Authorization": f"Bearer {token}",
        # "Content-Type": "application/json; charset=utf-8",
        # "tr_cd": tr_cd
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "tr_cd": tr_cd,
        "tr_cont": "N",
        "tr_cont_key": "",
    }
