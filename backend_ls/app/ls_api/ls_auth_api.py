import time
import requests
from backend_ls.app.core.ls_config_core import LS_APP_KEY, LS_TOKEN_URL, LS_APP_SECRET


class LSTokenManager:
    _access_token = None
    _expired_at = 0.0

    @classmethod
    def get_token(cls) -> str:
        now = time.time()
        if cls._access_token and now < cls._expired_at:
            return cls._access_token

        cls._issue_token()
        return cls._access_token

    @classmethod
    def _issue_token(cls):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {
            "grant_type": "client_credentials",
            "appkey": LS_APP_KEY,
            "appsecretkey": LS_APP_SECRET,
            "scope": "oob",
        }

        print("[LS] TOKEN URL =", LS_TOKEN_URL)

        res = requests.post(
            LS_TOKEN_URL,   # 🔥 그대로 사용
            headers=headers,
            data=payload,
            timeout=5,
        )

        if not res.ok:
            raise RuntimeError(
                f"LS token issue failed: {res.status_code} {res.text}"
            )

        data = res.json()
        cls._access_token = data["access_token"]
        cls._expired_at = time.time() + int(data["expires_in"]) - 30

        print("[LS] access token issued")
