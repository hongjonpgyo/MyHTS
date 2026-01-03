import os
from dotenv import load_dotenv

load_dotenv()

LS_APP_KEY = os.getenv("LS_APP_KEY")
LS_APP_SECRET = os.getenv("LS_APP_SECRET")
LS_BASE_URL = os.getenv("LS_BASE_URL")
LS_WS_URL = os.getenv("LS_WS_URL")

if not LS_APP_KEY or not LS_APP_SECRET:
    raise RuntimeError("❌ LS OpenAPI KEY/SECRET not set")
