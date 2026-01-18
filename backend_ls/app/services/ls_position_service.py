# backend_ls/app/services/ls_position_service.py

from sqlalchemy.orm import Session
from collections import defaultdict
from backend_ls.app.models.ls_futures_position_model import Position
from backend_ls.app.cache.ls_price_cache import ls_price_cache


class LSPositionService:

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
                "account_id": str(account_id),
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "side": "LONG" if pos.qty > 0 else "SHORT",

                "avg_price": float(pos.entry_price),
                "last_price": last_price,  # 🔥 이 줄 추가

                "unrealized_pnl": unrealized,
                "realized_pnl": float(pos.realized_pnl),
                "total_pnl": float(pos.realized_pnl) + unrealized,
                "liquidation_price": None,
            })

        return results
