import time
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
        "mac_address": ""
    }

    for idx, symbol in enumerate(symbols, start=1):
        body = {
            "o3105InBlock": {
                "symbol": symbol
            }
        }

        try:
            res = requests.post(url, headers=headers, json=body, timeout=10)

            if res.status_code != 200:
                raise RuntimeError(res.text)

            data = res.json()

            print(data)
            print("OUTBLOCK:", data.keys())
            out = data.get("o3105OutBlock")

            print(out)

            if out:
                rows.append(out)
                print(f"✔ 3105 OK [{symbol}]")
            else:
                print(f"⚠ 3105 EMPTY [{symbol}]")

        except Exception as e:
            # 🔥 핵심: 실패해도 절대 중단하지 않는다
            print(f"✘ 3105 SKIP [{symbol}] → {e}")
            failed.append(symbol)

        # -------------------------------------------------
        # 🔑 LS 호출 제한 대응 (핵심)
        # -------------------------------------------------
        time.sleep(0.25)   # 0.2~0.3 권장

        # 추가 안전장치: 일정 건수마다 숨 고르기
        if idx % 20 == 0:
            time.sleep(1.0)

    print(f"3105 RESULT → success={len(rows)}, failed={len(failed)}")
    return rows

if __name__ == "__main__":
    call_3105(['HSIG26  '])
