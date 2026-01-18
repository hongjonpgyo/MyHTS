import asyncio
import threading

from fastapi import FastAPI

# Routers
from backend_binance_old.api.orders_api import router as orders_router
from backend_binance_old.api.accounts_api import router as accounts_router
from backend_binance_old.api.positions_api import router as positions_router
from backend_binance_old.api.executions_api import router as executions_router
from backend_binance_old.api.symbols_api import router as symbols_router
from backend_binance_old.api.market_api import router as market_router
from backend_binance_old.api.market_ws_api import router as market_ws_router
from backend_binance_old.api.orderbook_api import router as orderbook_router
from backend_binance_old.api.auth_api import router as auth_router
from backend_binance_old.api.execution_ws_api import router as execution_ws_router
from backend_binance_old.api.account_ws_api import router as account_ws_router
from backend_binance_old.api.trades_ws_api import router as trades_ws_router
from backend_binance_old.api.orderbook_futures_api import router as orderbook_futures_router
from backend_binance_old.api.favorite_api import router as favorite_router
from backend_binance_old.api.routes.ls_market import router as ls_market_router

from backend_binance_old.config.symbol_registry import SYMBOL_REGISTRY
from backend_binance_old.config.settings import POLLING_INTERVAL

from backend_binance_old.db.database import SessionLocal
from backend_binance_old.services.market.futures_price_poller import YahooPriceThread

# Services
from backend_binance_old.services.market.market_service import market_service
from backend_binance_old.services.matching.matching_engine import MatchingEngine
from backend_binance_old.services.order_service import order_service

from backend_binance_old.config.settings import SYMBOLS_LIST
from backend_binance_old.config.settings import MATCHING_INTERVAL
from backend_binance_old.services.ws_broadcast import broadcast_manager


def create_app() -> FastAPI:
    """FastAPI 인스턴스를 생성하고 필요한 구성요소를 등록"""
    app = FastAPI(title="HTS Trading Backend")

    # -----------------------------
    # Router 등록
    # -----------------------------
    register_routers(app)

    # -----------------------------
    # Startup 이벤트 등록
    # -----------------------------
    # register_startup_events(app)

    return app


def register_routers(app: FastAPI):
    """모든 API 라우터를 앱에 등록"""
    app.include_router(auth_router)
    app.include_router(orders_router)
    app.include_router(accounts_router)
    app.include_router(positions_router)
    app.include_router(executions_router)
    app.include_router(symbols_router)
    app.include_router(market_router)
    app.include_router(market_ws_router)
    app.include_router(orderbook_router)
    app.include_router(execution_ws_router)
    app.include_router(account_ws_router)
    app.include_router(trades_ws_router)
    app.include_router(orderbook_futures_router)
    app.include_router(favorite_router)
    app.include_router(ls_market_router)

def register_startup_events(app: FastAPI):
    """시작 시 수행할 작업들을 정의"""
    engine = MatchingEngine()

    @app.on_event("startup")
    async def startup_event():
        print("🔥 MarketService Startup 시작")

        # 1) binance 심볼만 stream에 등록
        binance_symbols = [s for s, meta in SYMBOL_REGISTRY.items() if meta["price_source"] == "binance"]
        for sym in binance_symbols:
            market_service.add_symbol(sym)  # ✅ Binance WS 구독 대상만

        # 2) Binance WS 시작
        market_service.start()

        # 3) Yahoo futures poller 시작
        for sym, meta in SYMBOL_REGISTRY.items():
            if meta["price_source"] == "yahoo":
                poller = YahooPriceThread(
                    cache=market_service.cache,
                    symbol=sym,
                    yahoo_symbol=meta["yahoo_symbol"],
                    interval_sec=POLLING_INTERVAL
                )
                threading.Thread(target=poller.run, daemon=True).start()
                print(f"✅ Futures Poller started: {sym} ({meta['yahoo_symbol']})")

        print("🔥 MarketService Startup 완료")

        asyncio.create_task(matching_loop())
        asyncio.create_task(broadcast_manager.worker())

async def matching_loop():
    """ LIMIT 주문 자동 매칭 루프 """
    while True:
        try:
            db = SessionLocal()

            # ✅ binance + futures 모두 대상
            all_symbols = list(SYMBOL_REGISTRY.keys())

            for sym in all_symbols:
                await match_symbol(db, sym)

        except Exception as e:
            print("[MATCHING ERROR]", e)
        finally:
            db.close()

        await asyncio.sleep(MATCHING_INTERVAL)

async def match_symbol(db, symbol_code):
    # 현재 가격
    price_info = market_service.get_price(symbol_code)
    if not price_info:
        return

    bid = price_info["bid"]
    ask = price_info["ask"]

    # DB에서 OPEN 상태인 미체결 LIMIT 주문 가져오기
    orders = order_service.order_repo.get_open_orders_by_symbol(db, symbol_code)

    for od in orders:
        if od.side == "BUY":
            # BUY LIMIT: 주문가격 >= 현재 ASK → 체결
            if od.request_price >= ask:
                order_service.execute_limit_order(db, od, ask)

        else:  # SELL
            # SELL LIMIT: 주문가격 <= 현재 BID → 체결
            if od.request_price <= bid:
                order_service.execute_limit_order(db, od, bid)


# ==========================
# FastAPI Application
# ==========================
app = create_app()
