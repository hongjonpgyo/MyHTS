from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend_binance_old.db.database import get_db
from backend_binance_old.repositories.account_repo import account_repo

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = account_repo.get(db, account_id)
    if not account:
        return {"error": "Account not found"}
    return account
