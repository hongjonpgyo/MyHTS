from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_execution_model import Execution
from backend_ls.app.repositories.ls_futures_execution_repo import execution_repo
from backend_ls.app.realtime.execution_broadcast import ExecutionBroadcaster


class LSExecutionService:
    """
    Execution Service
    - 체결 기록의 단일 진실 소스
    - DB 기록 + 실시간 체결현황 push
    """

    # -------------------------------------------------
    # 내 주문 체결
    # -------------------------------------------------
    @staticmethod
    def record_my_execution(
        *,
        db: Session,
        account_id: int,
        order_id: int,
        symbol: str,
        side: str,
        price: float,
        qty: float,
        source: str = "ORDERBOOK",
    ) -> Execution:
        execution = Execution(
            account_id=account_id,
            order_id=order_id,
            symbol=symbol,
            side=side,
            price=price,
            qty=qty,
            exec_type="TRADE",
            source=source,
        )

        execution = execution_repo.insert(db, execution)

        # 🔔 실시간 체결현황 push
        ExecutionBroadcaster.publish(
            symbol=execution.symbol,
            side=execution.side,
            price=float(execution.price),
            qty=float(execution.qty),
            executed_at=execution.created_at,
            account_id=execution.account_id,
            order_id=execution.order_id,
        )

        return execution

    # -------------------------------------------------
    # 시장 체결 (내 주문 아님)
    # -------------------------------------------------
    @staticmethod
    def record_market_execution(
        *,
        db: Session,
        symbol: str,
        side: str,
        price: float,
        qty: float,
        source: str = "MARKET",
    ) -> Execution:
        execution = Execution(
            account_id=None,
            order_id=None,
            symbol=symbol,
            side=side,
            price=price,
            qty=qty,
            exec_type="TRADE",
            source=source,
        )

        execution = execution_repo.insert(db, execution)

        # 🔔 실시간 체결현황 push
        ExecutionBroadcaster.publish(
            symbol=execution.symbol,
            side=execution.side,
            price=float(execution.price),
            qty=float(execution.qty),
            executed_at=execution.created_at,
            account_id=None,
            order_id=None,
        )

        return execution

    @staticmethod
    def get_my_executions(
            db: Session,
            user_id: int,
            account_id: int,
            limit: int = 200,
    ):
        rows = (
            db.query(Execution)
            .filter(
                Execution.account_id == account_id
            )
            .order_by(Execution.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "exec_id": r.exec_id,
                "symbol": r.symbol,
                "side": r.side,
                "price": float(r.price),
                "qty": float(r.qty),
                "exec_type": r.exec_type,
                "source": r.source,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]


ls_execution_service = LSExecutionService()