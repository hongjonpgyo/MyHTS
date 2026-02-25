# backend_ls/app/repositories/ls_futures_protection_repo.py

from sqlalchemy.orm import Session
from backend_ls.app.models.ls_futures_protection_model import LSFuturesProtection


class ProtectionRepo:

    # -------------------------
    # Query
    # -------------------------
    @staticmethod
    def list_active_by_symbol(
        db: Session,
        account_id: int,
        symbol: str,
    ):
        return (
            db.query(LSFuturesProtection)
            .filter(
                LSFuturesProtection.account_id == account_id,
                LSFuturesProtection.symbol == symbol,
                LSFuturesProtection.is_active == True,
            )
            .all()
        )

    @staticmethod
    def list_active_by_account(
        db: Session,
        account_id: int,
    ):
        return (
            db.query(LSFuturesProtection)
            .filter(
                LSFuturesProtection.account_id == account_id,
                LSFuturesProtection.is_active == True,
            )
            .all()
        )

    # -------------------------
    # Deactivate (핵심)
    # -------------------------
    @staticmethod
    def deactivate(
        db: Session,
        protection_id: int,
    ) -> bool:
        updated = (
            db.query(LSFuturesProtection)
            .filter(
                LSFuturesProtection.id == protection_id,
                LSFuturesProtection.is_active == True,
            )
            .update(
                {"is_active": False},
                synchronize_session=False,
            )
        )
        return updated == 1

    @staticmethod
    def deactivate_group(
            db: Session,
            account_id: int,
            symbol: str,
            side: str,
    ) -> int:
        updated = (
            db.query(LSFuturesProtection)
            .filter(
                LSFuturesProtection.account_id == account_id,
                LSFuturesProtection.symbol == symbol,
                LSFuturesProtection.side == side,
                LSFuturesProtection.is_active == True,
            )
            .update(
                {"is_active": False},
                synchronize_session=False,
            )
        )
        return updated

    @staticmethod
    def deactivate_by_symbol(
        db: Session,
        account_id: int,
        symbol: str,
    ) -> int:
        """
        현 종목 전체 보호주문 해제
        (전체청산 / 심볼 전환 시 사용)
        """
        q = (
            db.query(LSFuturesProtection)
            .filter(
                LSFuturesProtection.account_id == account_id,
                LSFuturesProtection.symbol == symbol,
                LSFuturesProtection.is_active == True,
            )
        )

        count = q.count()
        q.update(
            {"is_active": False},
            synchronize_session=False,
        )
        return count

protection_repo = ProtectionRepo()