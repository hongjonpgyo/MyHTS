from decimal import Decimal
from sqlalchemy.orm import Session

from backend_binance_old.repositories.position_repo import position_repo
from backend_binance_old.models.account_model import Account
from backend_binance_old.models.symbol_model import Symbol
from backend_binance_old.models.position_model import Position


def F(v):
    """Decimal이든 str이든 무조건 float로 변환"""
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except:
        return 0.0


class PositionService:
    def __init__(self):
        self.position_repo = position_repo

    def handle_trade(
        self,
        db: Session,
        account: Account,
        symbol: Symbol,
        side: str,
        qty: float,
        exec_price: float,
    ) -> Position:

        # --------------------------------------------------
        # 기존 포지션 조회
        # --------------------------------------------------
        position = self.position_repo.get_by_account_symbol(
            db=db,
            account_id=account.account_id,
            symbol_id=symbol.symbol_id
        )

        signed_qty = F(qty if side.upper() == "BUY" else -qty)
        exec_price_f = F(exec_price)
        multiplier = F(symbol.multiplier)

        # --------------------------------------------------
        # 포지션이 없으면 신규 생성
        # --------------------------------------------------
        if position is None:
            position = self.position_repo.create(
                db=db,
                account_id=account.account_id,
                symbol_id=symbol.symbol_id,
                qty=signed_qty,
                entry_price=exec_price_f,
            )
            return position

        # 기존 포지션 값 → float 변환
        old_qty = F(position.qty)
        old_entry = F(position.entry_price)
        old_realized = F(position.realized_pnl)

        # --------------------------------------------------
        # Case 1: 같은 방향 → 포지션 증가
        # --------------------------------------------------
        if old_qty == 0 or (old_qty > 0 and signed_qty > 0) or (old_qty < 0 and signed_qty < 0):

            new_qty = F(old_qty + signed_qty)

            new_entry_price = F(
                (old_qty * old_entry + signed_qty * exec_price_f) / new_qty
            )

            return self.position_repo.update(
                db=db,
                position=position,
                qty=new_qty,
                entry_price=new_entry_price,
                realized_pnl=old_realized,
            )

        # --------------------------------------------------
        # Case 2: 반대 방향 → 청산 발생
        # --------------------------------------------------
        close_qty = min(abs(old_qty), abs(signed_qty))

        realized_pnl_delta = 0.0
        if old_qty > 0 and signed_qty < 0:
            realized_pnl_delta = F((exec_price_f - old_entry) * close_qty * multiplier)
        elif old_qty < 0 and signed_qty > 0:
            realized_pnl_delta = F((old_entry - exec_price_f) * close_qty * multiplier)

        remaining_qty = F(old_qty + signed_qty)

        # 완전 청산
        if abs(remaining_qty) < 1e-10:
            new_qty = 0.0
            new_entry_price = exec_price_f

        else:
            new_qty = remaining_qty

            # 일부 청산 → 방향 유지
            if (old_qty > 0 and remaining_qty > 0) or (old_qty < 0 and remaining_qty < 0):
                new_entry_price = old_entry
            else:
                # 반전된 경우 entry price = 이번 체결가
                new_entry_price = exec_price_f

        new_realized = F(old_realized + realized_pnl_delta)

        return self.position_repo.update(
            db=db,
            position=position,
            qty=new_qty,
            entry_price=F(new_entry_price),
            realized_pnl=new_realized,
        )


position_service = PositionService()
