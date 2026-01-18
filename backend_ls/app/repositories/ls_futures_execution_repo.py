from sqlalchemy.orm import Session

from backend_ls.app.models.ls_futures_execution_model import Execution


class LSExecutionRepo:
    """
    Execution Repository

    - 체결 데이터 단순 저장
    - 조회 로직은 Service / API에서 담당
    """

    # ----------------------------------
    # INSERT
    # ----------------------------------
    def insert(self, db: Session, execution: Execution) -> Execution:
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    # ----------------------------------
    # SELECT (체결현황용 – 선택)
    # ----------------------------------
    def get_recent_executions(
        self,
        db: Session,
        symbol: str,
        limit: int = 200,
    ):
        return (
            db.query(Execution)
            .filter(Execution.symbol == symbol)
            .order_by(Execution.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_my_executions(
        self,
        db: Session,
        account_id: int,
        symbol: str | None = None,
        limit: int = 200,
    ):
        q = db.query(Execution).filter(
            Execution.account_id == account_id
        )

        if symbol:
            q = q.filter(Execution.symbol == symbol)

        return (
            q.order_by(Execution.created_at.desc())
             .limit(limit)
             .all()
        )


# 싱글톤
execution_repo = LSExecutionRepo()
