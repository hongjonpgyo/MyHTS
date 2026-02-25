# backend_ls/app/services/ls_position_service.py

from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_position_model import Position
from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.models.ls_futures_protection_model import LSFuturesProtection
from backend_ls.app.repositories.ls_futures_reservation_repo import reservation_repo
from backend_ls.app.schemas.ls_order_schema import OrderCreate
from backend_ls.app.services.ls_order_service import LSOrderService


class LSPositionService:

    # ==========================================================
    # 단일 포지션 조회 (1계좌 1종목 1행 전제)
    # ==========================================================
    @staticmethod
    def get_position(db: Session, account_id: str, symbol: str) -> dict | None:

        pos = (
            db.query(Position)
            .filter(Position.account_id == int(account_id))
            .filter(Position.symbol == symbol)
            .first()
        )

        if not pos or pos.qty == 0:
            return None

        qty = Decimal(str(pos.qty))
        entry_price = Decimal(str(pos.entry_price))
        multiplier = Decimal(str(pos.multiplier))
        realized = Decimal(str(pos.realized_pnl))

        tick = ls_price_cache.get(symbol)
        last_price = Decimal(str(tick.price)) if tick else Decimal("0")

        # 🔥 승수 반영
        unrealized = (last_price - entry_price) * qty * multiplier

        return {
            "account_id": int(account_id),
            "symbol": symbol,
            "qty": float(qty),
            "side": "LONG" if qty > 0 else "SHORT",
            "avg_price": float(entry_price),
            "last_price": float(last_price),
            "unrealized_pnl": float(unrealized),
            "realized_pnl": float(realized),
            "total_pnl": float(realized + unrealized),
            "liquidation_price": None,
        }

    # ==========================================================
    # 전체 포지션 조회
    # ==========================================================
    @staticmethod
    def get_positions(db: Session, account_id: str):

        rows = (
            db.query(Position)
            .filter(Position.account_id == int(account_id))
            .all()
        )

        results = []

        for pos in rows:

            if pos.qty == 0:
                continue

            qty = Decimal(str(pos.qty))
            entry_price = Decimal(str(pos.entry_price))
            multiplier = Decimal(str(pos.multiplier))
            realized = Decimal(str(pos.realized_pnl))

            tick = ls_price_cache.get(pos.symbol)
            last_price = Decimal(str(tick.price)) if tick else Decimal("0")

            unrealized = (last_price - entry_price) * qty * multiplier

            results.append({
                "account_id": int(account_id),
                "symbol": pos.symbol,
                "qty": float(qty),
                "side": "LONG" if qty > 0 else "SHORT",
                "avg_price": float(entry_price),
                "last_price": float(last_price),
                "unrealized_pnl": float(unrealized),
                "realized_pnl": float(realized),
                "total_pnl": float(realized + unrealized),
                "liquidation_price": None,
            })

        return results

    # ==========================================================
    # 포지션 전량 청산
    # ==========================================================
    @staticmethod
    def close_position(db: Session, account_id: int, symbol: str, source: str = "UI"):

        pos = (
            db.query(Position)
            .filter(Position.account_id == account_id)
            .filter(Position.symbol == symbol)
            .first()
        )

        if not pos or pos.qty == 0:
            return {"ok": True, "reason": "NO_POSITION"}

        qty = Decimal(str(pos.qty))
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

            # 3️⃣ 시장가 청산 주문 생성 (commit 금지)
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