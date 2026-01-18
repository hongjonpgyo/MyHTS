import requests
from backend_ls.app.ls_api.ls_auth_api import LSTokenManager
from backend_ls.app.core import ls_config_core


def call_3105(symbols: list[str]):
    rows = []
    failed = []

    token = LSTokenManager.get_token()
    url = f"{ls_config_core.LS_BASE_URL}/overseas-futureoption/market-data"

    headers = {
        "content-type": "application/json;charset=utf-8",
        "authorization": f"Bearer {token}",
        "tr_cd": "o3105",
        "tr_cont": "N",
        "tr_cont_key": "",
        "mac_address":""
    }

    for symbol in symbols:
        body = {
            "o3105InBlock": {
                "symbol": symbol
            }
        }

        try:
            res = requests.post(url, headers=headers, json=body, timeout=10)
            print(res.status_code)
            if res.status_code != 200:
                raise RuntimeError(res.text)

            data = res.json()
            out = data.get("o3105OutBlock")

            if out:
                rows.append(out)
                print(f"✔ 3105 OK [{symbol}]")
            else:
                print(f"⚠ 3105 EMPTY [{symbol}]")

        except Exception as e:
            # 🔥 핵심: 절대 raise 하지 않는다
            print(f"✘ 3105 SKIP [{symbol}] → {e}")
            failed.append(symbol)
            continue

    print(f"3105 RESULT → success={len(rows)}, failed={len(failed)}")
    return rows
