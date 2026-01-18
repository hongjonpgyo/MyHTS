import os
from dotenv import load_dotenv

load_dotenv()

LS_APP_KEY = os.getenv("LS_APP_KEY")
LS_APP_SECRET = os.getenv("LS_APP_SECRET")

LS_BASE_URL = os.getenv("LS_BASE_URL")
LS_TOKEN_URL = os.getenv("LS_TOKEN_URL")
LS_WS_URL = os.getenv("LS_WS_URL")

if not LS_APP_KEY or not LS_APP_SECRET:
    raise RuntimeError("❌ LS OpenAPI KEY/SECRET not set")

if not LS_TOKEN_URL:
    raise RuntimeError("❌ LS_TOKEN_URL not set")

LS_TR_ENDPOINTS = {
    # 해외선물
    "o3101": f"{LS_BASE_URL}/overseas-futureoption/market-data",
    "o3105": f"{LS_BASE_URL}/overseas-futureoption/market-data",

    # 기타
    "t0167": f"{LS_BASE_URL}/etc/time-search",
}
SECRET_KEY = "CHANGE_ME_SECRET"  # TODO: 환경변수/설정에서 가져오도록 변경 권장
ALGORITHM = "HS256"