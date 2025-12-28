import asyncio
import time

from sqlalchemy.orm import Session

from backend.repositories.order_repo import OrderRepository
from backend.repositories.execution_repo import ExecutionRepository
from backend.repositories.position_repo import PositionRepository
from backend.repositories.symbol_repo import SymbolRepository
from backend.repositories.account_repo import AccountRepository

from backend.services.position_service import position_service
from backend.services.account_service import account_service
from backend.services.market.market_service import market_service
from backend.services.trade_stream import publish_trade

from backend.services.ws_broadcast import broadcast_manager


class OrderService:

    def __init__(self):
        self.order_repo = OrderRepository()
        self.exec_repo = ExecutionRepository()
        self.position_repo = PositionRepository()
        self.symbol_repo = SymbolRepository()
        self.account_repo = AccountRepository()

    def place_market_order(
            self,
            db: Session,
            account_id: int,
            symbol_code: str,
            side: str,
            qty: float
    ):
        account = self.account_repo.get(db, account_id)
        if not account:
            raise Exception("계좌 없음")

        symbol = self.symbol_repo.get_by_code(db, symbol_code)
        if not symbol:
            raise Exception("심볼 없음")

        # 실시간 가격
        price_info = market_service.get_price(symbol_code)
        if not price_info:
            raise Exception(f"{symbol_code} 실시간 가격 없음")

        exec_price = (
            price_info["ask"]
            if side.upper() == "BUY"
            else price_info["bid"]
        )

        # 1️⃣ 주문 생성 (Market)
        order = self.order_repo.create(
            db=db,
            account_id=account_id,
            symbol_id=symbol.symbol_id,
            side=side,
            qty=qty,
            request_price=None,
        )

        # 2️⃣ execution 생성
        execution = self.exec_repo.create(
            db=db,
            order_id=order.order_id,
            account_id=account.account_id,
            symbol_id=symbol.symbol_id,
            side=side,
            price=exec_price,
            qty=qty,
            fee=0.0
        )

        # 3️⃣ position 갱신
        position = position_service.handle_trade(
            db=db,
            account=account,
            symbol=symbol,
            side=side,
            qty=qty,
            exec_price=exec_price
        )

        # 4️⃣ 계좌 갱신
        account_service.update_after_trade(
            db=db,
            account=account,
            position=position,
            symbol=symbol
        )

        # 5️⃣ 주문 상태 FILLED
        self.order_repo.mark_filled(db, order)

        self._publish_account_update(db, account.account_id)

        # _process_fill 안, broadcast_trade 직전
        print(
            "[MATCH → TRADE : MARKET]",
            symbol.symbol_code,
            exec_price,
            order.qty,
            order.side
        )

        # 체결 직후
        trade_data = {
            "type": "trade",
            "symbol": symbol.symbol_code,
            "price": float(exec_price),
            "qty": float(order.qty),
            "side": order.side.upper(),
            "ts": time.time(),
        }

        publish_trade(symbol.symbol_code, trade_data)

        return {
            "ok": True,
            "order_id": order.order_id,
            "exec_price": float(exec_price),
            "position_qty": float(position.qty),
        }

    def place_limit_order(
            self,
            db: Session,
            account_id: int,
            symbol_code: str,
            side: str,
            qty: float,
            price: float
    ):
        """지정가 주문 생성 → 오더북에 쌓이고 체결되지 않음"""

        account = self.account_repo.get(db, account_id)
        if not account:
            raise Exception("계좌 없음")

        symbol = self.symbol_repo.get_by_code(db, symbol_code)
        if not symbol:
            raise Exception("심볼 없음")

        # order 생성 (status = OPEN)
        order = self.order_repo.create_limit(
            db=db,
            account_id=account_id,
            symbol_id=symbol.symbol_id,
            side=side,
            qty=qty,
            price=price
        )

        return {
            "ok": True,
            "order_id": order.order_id,
            "request_price": float(order.request_price),
            "status": order.status
        }

    # ------------------------------
    # OPEN LIMIT ORDERS 조회
    # ------------------------------
    # backend/services/order_service.py
    def get_open_orders(self, db: Session, account_id: int):
        orders = self.order_repo.get_open_orders(db, account_id)

        return [
            {
                "order_id": o.order_id,
                "symbol": o.symbol.symbol_code,  # ← join 후 정상 동작
                "side": o.side,
                "price": float(o.request_price or 0),
                "qty": float(o.qty),
                "status": o.status,
                "created_at": o.created_at.isoformat() if o.created_at else "",
            }
            for o in orders
        ]

    def cancel_orders(self, db: Session, order_ids: []):
        return self.order_repo.cancel_orders(db, order_ids)

    def execute_limit_order(self, db, order, exec_price):
        account = self.account_repo.get(db, order.account_id)
        symbol = order.symbol

        # 1️⃣ execution 생성
        execution = self.exec_repo.create(
            db=db,
            order_id=order.order_id,
            account_id=order.account_id,
            symbol_id=order.symbol_id,
            side=order.side,
            price=exec_price,
            qty=order.qty,
            fee=0.0
        )

        # 2️⃣ position 업데이트
        position = position_service.handle_trade(
            db=db,
            account=account,
            symbol=symbol,
            side=order.side,
            qty=order.qty,
            exec_price=exec_price
        )

        # 3️⃣ 계좌 업데이트
        account_service.update_after_trade(
            db=db,
            account=account,
            position=position,
            symbol=symbol
        )

        # 4️⃣ 주문 상태 FILLED
        self.order_repo.mark_filled(db, order)

        self._publish_account_update(db, account.account_id)

        # _process_fill 안, broadcast_trade 직전
        print(
            "[MATCH → TRADE : LIMIT]",
            symbol.symbol_code,
            exec_price,
            order.qty,
            order.side
        )

        # 체결 직후
        trade_data = {
            "type": "trade",
            "symbol": symbol.symbol_code,
            "price": float(exec_price),
            "qty": float(order.qty),
            "side": order.side.upper(),
            "ts": time.time(),
        }

        publish_trade(symbol.symbol_code, trade_data)

        return execution

    # backend/services/order_service.py (OrderService 안에 추가)
    def _publish_account_update(self, db: Session, account_id: int):
        account = self.account_repo.get(db, account_id)
        if not account:
            return

        positions = self.position_repo.get_by_account(db, account_id)

        pos_rows = []
        for p in positions:
            sym = p.symbol.symbol_code
            price_info = market_service.get_price(sym) or {}
            last_price = price_info.get("last") or price_info.get("price") or price_info.get("bid") or None

            qty = float(p.qty or 0)
            entry_price = float(p.entry_price or 0)
            multiplier = float(getattr(p.symbol, "multiplier", 1) or 1)

            if qty == 0 or last_price is None:
                upnl = 0.0
            else:
                lp = float(last_price)
                if qty > 0:
                    upnl = (lp - entry_price) * qty * multiplier
                else:
                    upnl = (entry_price - lp) * abs(qty) * multiplier

            liq = account_service.calc_liquidation_price(p, account, p.symbol)

            pos_rows.append({
                "symbol": sym,
                "side": ("LONG" if qty > 0 else "SHORT" if qty < 0 else ""),
                "qty": qty,
                "entry_price": entry_price,
                "unrealized_pnl": float(upnl),
                "liq_price": float(liq) if liq is not None else None,
            })

        account_row = {
            "balance": float(account.balance),
            "margin_used": float(account.margin_used),
            "margin_available": float(account.margin_available),
            "pnl_realized": float(account.pnl_realized),
            "pnl_unrealized": float(account.pnl_unrealized),
        }

        broadcast_manager.publish_account(
            account_id=account_id,
            message={
                "type": "account_update",
                "positions": pos_rows,
                "account": account_row,
            }
        )


order_service = OrderService()
