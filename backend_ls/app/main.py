from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend_ls.app.cache.symbol_meta_cache import symbol_meta_cache, SymbolMeta
from backend_ls.app.core.ls_tick_queue_engine import ls_tick_queue_engine
from backend_ls.app.ls_api.ls_ws_client_api import LSWebSocketClient
from backend_ls.app.routers.ls_futures_router import router as ls_futures_router
from backend_ls.app.routers.ls_futures_admin_router import router as ls_futures_admin_router
from backend_ls.app.core import ls_realtime_manager

from backend_ls.app.services.fx.exim_fx_loader import load_daily_fx

# 추가
from backend_ls.app.ls_api.tr_3105 import call_3105
from backend_ls.app.services.ls_futures_raw_3105_service import LSFuturesRaw3105Service
from backend_ls.app.db.ls_db import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan

    STARTUP
    - FX 로딩
    - Futures Metadata 로딩 (3105)
    - LS WebSocket 연결

    SHUTDOWN
    - WS 종료
    """

    print("[APP] startup")
    ls_tick_queue_engine.start()

    # ---------------------------------
    # 1 FX 로딩
    # ---------------------------------
    try:
        load_daily_fx()
        print("[FX] loaded")
    except Exception as e:
        print("[FX] load error:", e)

    # ---------------------------------
    # 2 Futures Metadata (3105)
    # ---------------------------------
    try:
        print("[3105] loading futures metadata")

        db = SessionLocal()

        symbols = [
            "ESH26",
            "HMHH26",
            "HSIH26",
            "MNQH26",
            "NQH26",
        ]

        rows = call_3105(symbols)

        count = LSFuturesRaw3105Service.upsert_from_3105(db, rows)

        print(f"[3105] upsert complete ({count} symbols)")

        for r in rows:
            symbol = r.get("Symbol")

            tick_size = float(
                r.get("UntPrc")
                or 1
            )

            multiplier = float(
                r.get("CtrtPrAmt")
                or 1
            )

            symbol_meta_cache.set(
                symbol,
                SymbolMeta(
                    symbol,
                    tick_size,
                    multiplier
                )
            )

            print("[META CACHE]", symbol, tick_size, multiplier)

    except Exception as e:
        print("[3105] load error:", e)

    finally:
        try:
            db.close()
        except:
            pass

    # ---------------------------------
    # 3 LS WebSocket 시작
    # ---------------------------------
    try:
        ls_realtime_manager.ls_ws_client = LSWebSocketClient()
        ls_realtime_manager.ls_ws_client.start()
        print("[LS WS] started")

    except Exception as e:
        print("[LS WS] startup error:", e)
        raise

    # 서버 실행
    yield

    # =================================
    # SHUTDOWN
    # =================================
    print("[APP] shutdown")

    if ls_realtime_manager.ls_ws_client:

        try:
            ls_realtime_manager.ls_ws_client.stop()
            print("[LS WS] stopped")

        except Exception as e:
            print("[LS WS] shutdown error:", e)

        ls_realtime_manager.ls_ws_client = None


# ---------------------------------
# FastAPI App
# ---------------------------------
app = FastAPI(
    title="LS Futures Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------
# Router
# ---------------------------------
app.include_router(ls_futures_router)
app.include_router(ls_futures_admin_router)


# ---------------------------------
# Health Check
# ---------------------------------
@app.get("/health")
def health_check():
    ws = ls_realtime_manager.ls_ws_client

    return {
        "status": "ok",
        "ls_ws_connected": bool(ws and ws.connected),
        "ls_ws_subscribed": len(ws.subscribed) if ws else 0,
    }