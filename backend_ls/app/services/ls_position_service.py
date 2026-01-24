# backend_ls/app/services/ls_position_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict
from backend_ls.app.models.ls_futures_position_model import Position
from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.models.ls_futures_protection_model import LSFuturesProtection
from backend_ls.app.repositories.ls_futures_reservation_repo import reservation_repo
from backend_ls.app.schemas.ls_order_schema import OrderCreate
from backend_ls.app.services.ls_order_service import LSOrderService


class LSPositionService:

    @staticmethod
    def get_position(db: Session, account_id: str, symbol: str) -> dict | None:
        rows = (
            db.query(Position)
            .filter(Position.account_id == int(account_id))
            .filter(Position.symbol == symbol)
            .all()
        )

        if not rows:
            return None

        qty = 0.0
        cost = 0.0
        realized = 0.0

        for p in rows:
            qty += float(p.qty)
            cost += float(p.qty) * float(p.entry_price)
            realized += float(p.realized_pnl)

        if qty == 0:
            return None  # 전량 청산된 상태

        avg_price = cost / qty

        tick = ls_price_cache.get(symbol)
        last_price = float(tick.price) if tick else 0.0
        unrealized = (last_price - avg_price) * qty

        return {
            "account_id": int(account_id),
            "symbol": symbol,
            "qty": qty,
            "side": "LONG" if qty > 0 else "SHORT",
            "avg_price": avg_price,
            "last_price": last_price,
            "unrealized_pnl": unrealized,
            "realized_pnl": realized,
            "total_pnl": realized + unrealized,
            "liquidation_price": None,
        }

    @staticmethod
    def get_positions(db: Session, account_id: str):
        rows = (
            db.query(Position)
            .filter(Position.account_id == int(account_id))
            .all()
        )

        grouped = defaultdict(lambda: {
            "qty": 0.0,
            "cost": 0.0,
            "realized_pnl": 0.0,
        })

        # -------------------------------------------------
        # 1️⃣ 포지션 집계 (symbol 기준)
        # -------------------------------------------------
        for pos in rows:
            g = grouped[pos.symbol]
            g["qty"] += float(pos.qty)
            g["cost"] += float(pos.qty) * float(pos.entry_price)
            g["realized_pnl"] += float(pos.realized_pnl)

        results = []

        # -------------------------------------------------
        # 2️⃣ 종목별 결과 생성
        # -------------------------------------------------
        for symbol, g in grouped.items():
            qty = g["qty"]
            if qty == 0:
                continue  # 🔥 전량 청산된 포지션 제거

            avg_price = g["cost"] / qty

            tick = ls_price_cache.get(symbol)
            last_price = float(tick.price) if tick else 0.0

            unrealized = (last_price - avg_price) * qty

            results.append({
                "account_id": int(account_id),
                "symbol": symbol,
                "qty": qty,
                "side": "LONG" if qty > 0 else "SHORT",
                "avg_price": avg_price,
                "last_price": last_price,
                "unrealized_pnl": unrealized,
                "realized_pnl": g["realized_pnl"],
                "total_pnl": g["realized_pnl"] + unrealized,
                "liquidation_price": None,
            })

        return results

    @staticmethod
    def close_position(db: Session, account_id: int, symbol: str, source: str = "UI"):
        pos = LSPositionService.get_position(db, str(account_id), symbol)
        if not pos:
            return {"ok": True, "reason": "NO_POSITION"}

        qty = float(pos["qty"])
        if qty == 0:
            return {"ok": True, "reason": "QTY_ZERO"}

        close_qty = abs(int(qty))
        side = "SELL" if qty > 0 else "BUY"

        try:
            # 1️⃣ 예약 취소
            cancelled = reservation_repo.cancel_waiting_by_symbol(
                db, account_id, symbol
            )

            # 2️⃣ 보호 비활성화
            prot_q = (
                db.query(LSFuturesProtection)
                .filter(
                    LSFuturesProtection.account_id == account_id,
                    LSFuturesProtection.symbol == symbol,
                    LSFuturesProtection.is_active == True,
                )
            )
            deactivated = prot_q.count()
            prot_q.update({"is_active": False}, synchronize_session=False)

            # 3️⃣ 시장가 청산 주문 (❌ commit 금지)
            payload = OrderCreate(
                account_id=account_id,
                symbol=symbol,
                side=side,
                order_type="MARKET",
                qty=close_qty,
                request_price=None,
                source=source,
            )
            order = LSOrderService.create_order(db, payload)

            # 4️⃣ 단일 commit
            db.commit()

            return {
                "ok": True,
                "symbol": symbol,
                "closed_side": side,
                "closed_qty": close_qty,
                "cancelled_reservations": cancelled,
                "deactivated_protections": deactivated,
                "created_order_id": order.order_id,
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(400, f"close_position failed: {e}")

