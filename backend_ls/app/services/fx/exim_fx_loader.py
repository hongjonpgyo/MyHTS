# services/fx/exim_fx_loader.py
import requests
from datetime import date
from backend_ls.app.core import global_rates

EXIM_URL = "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
AUTH_KEY = "zCgfzAFjaA42gSTtjSyDCrRBjhD0bRun"

def load_daily_fx():
    today = date.today().strftime("%Y%m%d")

    res = requests.get(
        EXIM_URL,
        params={
            "authkey": AUTH_KEY,
            "searchdate": today,
            "data": "AP01",
        },
        timeout=5,
    )

    res.raise_for_status()

    rates = {}
    for r in res.json():
        cur = r["cur_unit"]
        rate = float(r["deal_bas_r"].replace(",", ""))
        rates[cur] = rate

    global_rates.FX_RATES.clear()
    global_rates.FX_RATES.update(rates)
    global_rates.FX_DATE = date.today()

    print(global_rates.FX_RATES)
