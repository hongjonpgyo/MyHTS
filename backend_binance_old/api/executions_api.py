from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend_binance_old.db.database import get_db
from backend_binance_old.services.execution_service import ExecutionService

router = APIRouter(prefix="/executions", tags=["Executions"])

service = ExecutionService()


@router.get("/my/{account_id}")
def get_executions(account_id: int, db: Session = Depends(get_db)):
    return service.get_account_executions(db, account_id)
