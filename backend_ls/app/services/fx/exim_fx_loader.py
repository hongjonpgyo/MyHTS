# services/fx/exim_fx_loader.py
import requests
from datetime import date, timedelta
from backend_ls.app.core import global_rates

EXIM_URL = "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
AUTH_KEY = "zCgfzAFjaA42gSTtjSyDCrRBjhD0bRun"


def _fetch_fx_for_date(target_date: date):
    """특정 날짜 환율 조회"""

    try:
        res = requests.get(
            EXIM_URL,
            params={
                "authkey": AUTH_KEY,
                "searchdate": target_date.strftime("%Y%m%d"),
                "data": "AP01",
            },
            timeout=5,
        )

        res.raise_for_status()
        data = res.json()

        if not data:
            return None

        rates = {}

        for r in data:

            cur = r.get("cur_unit")

            if cur in ("HKD", "USD"):

                rate = float(r["deal_bas_r"].replace(",", ""))

                rates[cur] = rate

        return rates if rates else None

    except Exception as e:
        print(f"❌ 환율 조회 실패 ({target_date}):", e)
        return None


def load_daily_fx():

    print("🔄 환율 로딩 시도...")

    today = date.today()

    for i in range(7):  # 최근 7일 탐색

        target = today - timedelta(days=i)

        rates = _fetch_fx_for_date(target)

        if rates:

            for cur, rate in rates.items():
                global_rates.FX_RATES[cur] = rate

            global_rates.FX_DATE = target

            print(
                f"✅ 환율 적용: {rates} (기준일 {target})"
            )

            return

        print(f"⚠ {target} 환율 없음")

    print("❌ 최근 7일 내 환율 없음 → 기존 환율 유지")