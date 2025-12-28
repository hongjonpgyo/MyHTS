# backend/services/matching/matching_engine.py

import traceback
import asyncio
import time

from backend.db.database import SessionLocal

from backend.repositories.order_repo import OrderRepository
from backend.repositories.execution_repo import ExecutionRepository
from backend.repositories.position_repo import PositionRepository
from backend.repositories.symbol_repo import SymbolRepository

from backend.services.market.market_service import market_service
from backend.services.account_service import account_service
from backend.services.position_service import position_service
from backend.services.notifier.execution_notifier import execution_notifier
from backend.services.ws_broadcast import broadcast_manager

from backend.utils.num import _f


class MatchingEngine:

    def __init__(self):
        self.order_repo = OrderRepository()
        self.exec_repo = ExecutionRepository()
        self.position_repo = PositionRepository()
        self.symbol_repo = SymbolRepository()

    # ==========================================================
    # 지정가 주문 매칭
    # ==========================================================
    def match_symbol(self, db, symbol_code):
        try:
            symbol = self.symbol_repo.get_by_code(db, symbol_code)
            if not symbol:
                return

            symbol_id = symbol.symbol_id

            # 현재 가격
            price_info = market_service.get_price(symbol_code)
            if not price_info:
                return

            bid = _f(price_info.get("bid"))
            ask = _f(price_info.get("ask"))

            # 미체결 주문
            open_orders = self.order_repo.get_open_orders_by_symbol(db, symbol_id)
            if not open_orders:
                return

            filled_ids = []

            # 매칭 로직
            for o in open_orders:

                req_price = _f(o.request_price)
                qty = _f(o.qty)
                side = o.side.upper()

                if side == "BUY" and req_price >= ask:
                    self._process_fill(db, o, ask, qty)
                    filled_ids.append(o.order_id)

                elif side == "SELL" and req_price <= bid:
                    self._process_fill(db, o, bid, qty)
                    filled_ids.append(o.order_id)

            return filled_ids

        except Exception:
            print("[MATCHING ERROR]", traceback.format_exc())

    # ==========================================================
    # 체결 처리 (float 강제 적용)
    # ==========================================================
    def _process_fill(self, db, order, exec_price, qty):

        exec_price = _f(exec_price)
        qty = _f(qty)

        account = order.account
        symbol = order.symbol

        # 🔥 모든 필드 float 변환
        account.balance = _f(account.balance)
        account.margin_used = _f(account.margin_used)
        account.margin_available = _f(account.margin_available)

        # 주문 상태 변경
        order.exec_price = exec_price
        order.filled_qty = qty

        self.order_repo.mark_filled(db, order)

        # execution 생성
        execution = self.exec_repo.create(
            db=db,
            order_id=order.order_id,
            account_id=account.account_id,
            symbol_id=symbol.symbol_id,
            side=order.side,
            price=exec_price,
            qty=qty,
            fee=0.0,
        )

        # 포지션 갱신 (여기에서도 Decimal 발생 방지)
        position = position_service.handle_trade(
            db=db,
            account=account,
            symbol=symbol,
            side=order.side,
            qty=qty,
            exec_price=exec_price,
        )

        # 계좌 갱신
        account_service.update_after_trade(
            db=db,
            account=account,
            position=position,
            symbol=symbol,
        )

        # _process_fill 안, broadcast_trade 직전
        print(
            "[MATCH → TRADE]",
            symbol.symbol_code,
            exec_price,
            qty,
            order.side
        )

        broadcast_manager.publish_trade(
            symbol.symbol_code,
            {
                "symbol": symbol.symbol_code,  # BTCUSDT
                "price": exec_price,
                "qty": qty,
                "side": order.side.upper(),  # BUY / SELL
                "ts": time.time(),  # unix timestamp
            }
        )

        # # =================================================
        # # 🔥 1️⃣ Time & Sales 브로드캐스트 (NEW)
        # # =================================================
        # trade_data = {
        #     "type": "trade",  # ❗ 프론트 필터용
        #     "symbol": symbol.symbol_code,  # BTCUSDT
        #     "price": exec_price,
        #     "qty": qty,
        #     "side": order.side.upper(),  # BUY / SELL
        #     "ts": time.time(),  # timestamp
        # }
        #
        # asyncio.create_task(
        #     broadcast_trade(trade_data)
        # )
        #
        # # -----------------------------------------
        # # 🔥 WebSocket Push 알림
        # # -----------------------------------------
        # execution_data = {
        #     "order_id": order.order_id,
        #     "symbol": symbol.symbol_code,
        #     "side": order.side,
        #     "price": exec_price,
        #     "qty": qty,
        #     "type": "AUTO",
        #     "created_at": execution.created_at.isoformat(),
        # }
        #
        # asyncio.get_event_loop().create_task(
        #     execution_notifier.broadcast(account.account_id, execution_data)
        # )
        #
        # asyncio.create_task(
        #     broadcast_manager.send(
        #         order.account_id,
        #         {
        #             "type": "execution",
        #             "symbol": order.symbol.symbol_code,
        #             "side": order.side,
        #             "price": exec_price,
        #             "qty": qty
        #         }
        #     )
        # )

    # ==========================================================
    # 전체 종목 매칭
    # ==========================================================
    def match_all(self):
        db = SessionLocal()
        try:
            symbols = market_service.get_all_symbols()
            for sym in symbols:
                self.match_symbol(db, sym)
            db.commit()
        except Exception:
            db.rollback()
            print("[MATCH ALL ERROR]", traceback.format_exc())
        finally:
            db.close()


matching_engine = MatchingEngine()
