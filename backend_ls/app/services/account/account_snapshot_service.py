# services/account/account_snapshot_service.py

from decimal import Decimal
from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.repositories.ls_futures_position_repo import positionRepo
from backend_ls.app.repositories.ls_futures_account_repo import account_repo


# backend_ls/app/services/account/account_snapshot_service.py

from decimal import Decimal
from sqlalchemy.orm import Session

from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.repositories.ls_futures_position_repo import positionRepo
from backend_ls.app.services.ls_account_service import LSAccountService

# backend_ls/app/services/account/account_snapshot_service.py

from decimal import Decimal
from sqlalchemy.orm import Session

from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.repositories.ls_futures_position_repo import positionRepo
from backend_ls.app.services.ls_account_service import LSAccountService


class AccountSnapshotService:

    @staticmethod
    def calculate(db: Session, account_id: int):

        # ---------------------------------
        # 1️⃣ 예탁금 조회
        # ---------------------------------
        account_row = LSAccountService.get_balance(db, account_id)

        if not account_row:
            return {
                "account_id": account_id,
                "deposit": 0.0,
                "used_margin": 0.0,
                "available": 0.0,
                "unrealized_pnl": 0.0,
                "unrealized_pnl_rate": 0.0,
                "equity": 0.0,
            }

        deposit = Decimal(str(account_row.balance or 0))

        # ---------------------------------
        # 2️⃣ 포지션 조회
        # ---------------------------------
        positions = positionRepo.get_by_account(db, account_id)

        total_unrealized = Decimal("0")
        total_used_margin = Decimal("0")
        total_position_value = Decimal("0")

        # ---------------------------------
        # 3️⃣ 포지션별 계산
        # ---------------------------------
        for pos in positions:

            qty = Decimal(str(pos.qty or 0))
            if qty == 0:
                continue

            entry_price = Decimal(str(pos.entry_price or 0))
            multiplier = Decimal(str(pos.multiplier or 1))
            opng_mgn = Decimal(str(pos.opng_mgn or 0))

            # 🔥 사용증거금 (가격 없어도 계산됨)
            used_margin = abs(qty) * opng_mgn
            total_used_margin += used_margin

            # 🔥 현재가 조회
            current_price = ls_price_cache.get_last_price(pos.symbol)

            if current_price is not None:
                current_price = Decimal(str(current_price))

                pnl = (current_price - entry_price) * qty * multiplier
                total_unrealized += pnl

                total_position_value += abs(entry_price * qty * multiplier)

        # ---------------------------------
        # 4️⃣ 계좌 요약 계산
        # ---------------------------------
        equity = deposit + total_unrealized
        available = equity - total_used_margin

        pnl_rate = (
            (total_unrealized / total_position_value) * Decimal("100")
            if total_position_value != 0
            else Decimal("0")
        )

        # ---------------------------------
        # 5️⃣ 반환
        # ---------------------------------
        return {
            "account_id": account_id,
            "deposit": float(deposit),
            "used_margin": float(total_used_margin),
            "available": float(available),
            "unrealized_pnl": float(total_unrealized),
            "unrealized_pnl_rate": float(pnl_rate),
            "equity": float(equity),
        }