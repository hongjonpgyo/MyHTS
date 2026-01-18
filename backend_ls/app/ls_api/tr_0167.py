# backend_ls/app/ls_api/tr_t0167.py
from backend_ls.app.ls_api.ls_client_api import LSClient

def call_t0167():
    res = LSClient.call(
        tr_cd="t0167",
        body={}
    )
    return res.get("t0167OutBlock", {})
