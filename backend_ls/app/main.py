from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend_ls.app.ls_api.ls_ws_client_api import LSWebSocketClient
from backend_ls.app.routers.ls_futures_router import router as ls_futures_router
from backend_ls.app.core import ls_realtime_manager
from backend_ls.app.services.fx.exim_fx_loader import load_daily_fx

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan
    - 서버 시작 시 LS WebSocket 연결
    - 서버 종료 시 정리
    """
    print("[APP] startup")

    try:
        ls_realtime_manager.ls_ws_client = LSWebSocketClient()
        ls_realtime_manager.ls_ws_client.connect()
        print("[LS WS] started")
    except Exception as e:
        print("[LS WS] startup error:", e)
        raise

    load_daily_fx()
    # 서버 실행 구간
    yield

    # =====================
    # SHUTDOWN
    # =====================
    print("[APP] shutdown")

    if ls_realtime_manager.ls_ws_client:
        try:
            ls_realtime_manager.ls_ws_client.close()
            print("[LS WS] stopped")
        except Exception as e:
            print("[LS WS] shutdown error:", e)

        ls_realtime_manager.ls_ws_client = None


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
# Health Check
# -------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}
