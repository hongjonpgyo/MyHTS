# backend_ls/app/ls_api/ls_client_api.py

import requests
from backend_ls.app.ls_api.ls_auth_api import LSTokenManager
from backend_ls.app.core.ls_config_core import LS_TR_ENDPOINTS


class LSClient:

    @classmethod
    def call(cls, tr_cd: str, body: dict):
        token = LSTokenManager.get_token()

        if tr_cd not in LS_TR_ENDPOINTS:
            raise RuntimeError(f"Unknown TR code: {tr_cd}")

        url = LS_TR_ENDPOINTS[tr_cd]

        headers = {
            "content-type": "application/json;charset=utf-8",
            "authorization": f"Bearer {token}",
            "tr_cd": tr_cd,
            "tr_cont": "N",
            "mac_address": "000000000000",
        }

        res = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=10,
        )

        if res.status_code != 200:
            raise RuntimeError(
                f"LS API failed [{tr_cd}]: {res.status_code} {res.text}"
            )

        return res.json()
