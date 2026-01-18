from sqlalchemy.orm import Session
from backend_binance_old.models.account_model import Account


class AccountRepository:

    def get(self, db: Session, account_id: int):
        return db.query(Account).filter(Account.account_id == account_id).first()

    def create(self, db: Session, user_id: int):
        account = Account(user_id=user_id)
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    def update_balance(self, db: Session, account: Account,
                       balance=None, margin_used=None,
                       margin_available=None,
                       pnl_realized=None, pnl_unrealized=None):

        if balance is not None:
            account.balance = balance
        if margin_used is not None:
            account.margin_used = margin_used
        if margin_available is not None:
            account.margin_available = margin_available
        if pnl_realized is not None:
            account.pnl_realized = pnl_realized
        if pnl_unrealized is not None:
            account.pnl_unrealized = pnl_unrealized

        db.commit()
        db.refresh(account)
        return account

    def get_primary_account(self, db: Session, user_id: int) -> Account | None:
        # 일단 user_id 기준 첫 계좌를 primary로 사용
        return (
            db.query(Account)
            .filter(Account.user_id == user_id)
            .order_by(Account.account_id.asc())
            .first()
        )

account_repo = AccountRepository()
