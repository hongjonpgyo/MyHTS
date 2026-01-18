# backend_ls/app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI

# -------------------------
# Routers
# -------------------------
from backend_ls.app.routers.ls_futures_router import router as ls_futures_router

# -------------------------
# LS WebSocket
# -------------------------
from backend_ls.app.ls_api.ls_ws_client_api import LSWebSocketClient


# 전역 WS 클라이언트 (서버 전체 1개)
ls_ws_client: LSWebSocketClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan
    - 서버 시작 시 LS WebSocket 연결
    - 서버 종료 시 정리
    """
    global ls_ws_client

    # =====================
    # STARTUP
    # =====================
    print("[APP] startup")

    try:
        ls_ws_client = LSWebSocketClient()
        ls_ws_client.connect()

        # 🔥 초기 구독 (테스트용 / 추후 자동화 가능)
        ls_ws_client.subscribe("OVC", "HSIF26")
        # ls_ws_client.subscribe("OVC", "HTIF26")

        print("[LS WS] started")

    except Exception as e:
        print("[LS WS] startup error:", e)
        raise

    # 서버 실행 구간
    yield

    # =====================
    # SHUTDOWN
    # =====================
    print("[APP] shutdown")

    if ls_ws_client:
        try:
            ls_ws_client.close()
            print("[LS WS] stopped")
        except Exception as e:
            print("[LS WS] shutdown error:", e)

        ls_ws_client = None


# -------------------------
# FastAPI App
# -------------------------
app = FastAPI(
    title="LS Futures Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# -------------------------
# Router 등록
# -------------------------
app.include_router(ls_futures_router)

# -------------------------
# Health Check (선택)
# -------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}
