from backend_binance_old.models.execution_model import Execution
from backend_binance_old.models.symbol_model import Symbol
from sqlalchemy.orm import Session


class ExecutionRepository:
    # ------------------------------------------------------
    # 체결 저장
    # ------------------------------------------------------
    def create(self, db: Session,
               order_id: int,
               account_id: int,
               symbol_id: int,
               side: str,
               price: float,
               qty: float,
               fee: float):
        execution = Execution(
            order_id=order_id,
            account_id=account_id,
            symbol_id=symbol_id,
            side=side,
            price=price,
            qty=qty,
            fee=fee,
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def save_execution(self, db: Session, order, price, qty, fee=0, exec_type="TRADE"):
        row = Execution(
            order_id=order.order_id,
            account_id=order.account_id,
            symbol_id=order.symbol_id,
            side=order.side,
            price=price,
            qty=qty,
            fee=fee,
            exec_type=exec_type
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    def get_by_account(self, db: Session, account_id: int):
        return (
            db.query(Execution, Symbol.symbol_code)
            .join(Symbol, Symbol.symbol_id == Execution.symbol_id)
            .filter(Execution.account_id == account_id)
            .order_by(Execution.exec_id.desc())
            .all()
        )
