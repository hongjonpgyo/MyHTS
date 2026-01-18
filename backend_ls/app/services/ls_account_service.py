# backend_ls/app/services/ls_account_service.py

from sqlalchemy.orm import Session
from backend_ls.app.models.ls_futures_account_balance_model import LSAccountBalance

class LSAccountService:

    @staticmethod
    def get_balance(db: Session, account_id: str):
        return (
            db.query(LSAccountBalance)
            .filter(LSAccountBalance.account_id == account_id)
            .first()
        )