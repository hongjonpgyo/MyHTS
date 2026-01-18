from backend_binance_old.repositories.execution_repo import ExecutionRepository


class ExecutionService:

    def __init__(self):
        self.repo = ExecutionRepository()

    def record_execution(self, db, order, price, qty, fee=0, exec_type="TRADE"):
        return self.repo.save_execution(db, order, price, qty, fee, exec_type)

    def get_account_executions(self, db, account_id):
        data = self.repo.get_by_account(db, account_id)

        # repo가 (Execution, symbol_code) 튜플 반환하므로 변환 필요
        return [
            {
                "exec_id": r.Execution.exec_id,
                "order_id": r.Execution.order_id,
                "symbol": r.symbol_code,
                "side": r.Execution.side,
                "price": float(r.Execution.price),
                "qty": float(r.Execution.qty),
                "fee": float(r.Execution.fee),
                "type": r.Execution.exec_type,
                "created_at": r.Execution.created_at.isoformat() if r.Execution.created_at else "",
            }
            for r in data
        ]
