# services/ls_auth_service.py
import requests
from backend_binance_old.config.ls_settings import LS_APP_KEY, LS_APP_SECRET, LS_BASE_URL

class LSAuthService:
    _access_token = None

    @classmethod
    def get_token(cls):
        if cls._access_token:
            return cls._access_token

        url = f"{LS_BASE_URL}/oauth2/token"

        url = "https://openapi.ls-sec.co.kr:8080/oauth2/token"

        data = {
            "grant_type": "client_credentials",
            "appkey": "PSnfXVDGywhF58V74t3QDaZXzgVKshD49Gxj",
            "appsecretkey": "ln5S4NaXcZMXvRur6cU08UrQhHnIbRNG",
            "scope": "oob",
        }

        r = requests.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )

        print(r)

        r.raise_for_status()

        data = r.json()
        print(data)
        cls._access_token = data["access_token"]
        return cls._access_token
