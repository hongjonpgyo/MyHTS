from sqlalchemy.orm import Session, joinedload
from backend_binance_old.models.order_model import Order
from backend_binance_old.models.symbol_model import Symbol

class OrderRepository:

    def get(self, db: Session, order_id: int):
        return db.query(Order).filter(Order.order_id == order_id).first()

    def get_by_account(self, db: Session, account_id: int):
        return db.query(Order).filter(Order.account_id == account_id).all()

    def create(self, db: Session, account_id: int, symbol_id: int,
               side: str, qty: float, request_price=None):

        order = Order(
            account_id=account_id,
            symbol_id=symbol_id,
            side=side,
            qty=qty,
            request_price=request_price,
            order_type="MARKET",     # 현재는 MARKET 고정
            status="FILLED",          # 즉시 체결 HTS 구조
            reason="NORMAL"
        )

        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def create_limit(self, db: Session, account_id: int, symbol_id: int,
                     side: str, qty: float, price: float):
        order = Order(
            account_id=account_id,
            symbol_id=symbol_id,
            side=side,
            qty=qty,
            request_price=price,
            status="OPEN",
            order_type="LIMIT",
            reason="NORMAL"
        )

        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def update_exec_price(self, db: Session, order: Order, price: float):
        order.exec_price = price
        db.commit()
        db.refresh(order)
        return order

    # ---------------------------------------------------------
    # READ: 계좌의 OPEN 상태 LIMIT 주문 조회
    # ---------------------------------------------------------
    def get_open_orders(self, db: Session, account_id: int):
        orders = (
            db.query(Order)
            .join(Symbol, Order.symbol_id == Symbol.symbol_id)
            .options(joinedload(Order.symbol))
            .filter(Order.account_id == account_id, Order.status == "OPEN")
            .order_by(Order.order_id.desc())
            .all()
        )
        return orders

    # ---------------------------------------------------------
    # CANCEL: 주문 취소
    # ---------------------------------------------------------
    def cancel_orders(self, db: Session, order_ids: list[int]):
        """
        여러 주문을 한 번에 취소한다.
        조건:
        - OPEN 상태인 주문만 취소 가능
        """
        cancelled = (
            db.query(Order)
            .filter(
                Order.order_id.in_(order_ids),
                Order.status == "OPEN"
            )
            .all()
        )

        for o in cancelled:
            o.status = "CANCELLED"

        db.commit()
        return [o.order_id for o in cancelled]

    # backend_binance_old/repositories/order_repo.py

    def get_all_open_limit_orders(self, db: Session):
        return db.query(Order).filter(
            Order.status == "OPEN",
            Order.order_type == "LIMIT"
        ).all()

    # ----------------------------------------------------------
    # 🔥 (NEW) 심볼 기준 OPEN 주문 조회 → MatchingEngine에서 사용
    # ----------------------------------------------------------
    def get_open_orders_by_symbol(self, db: Session, symbol):
        # symbol이 문자열(symbol_code)인 경우 ID로 변환
        from backend_binance_old.repositories.symbol_repo import SymbolRepository
        symbol_repo = SymbolRepository()

        if isinstance(symbol, str):  # "BTCUSDT"
            symbol_obj = symbol_repo.get_by_code(db, symbol)
            if not symbol_obj:
                return []
            symbol = symbol_obj.symbol_id  # 정수로 변환

        return (
            db.query(Order)
            .filter(
                Order.symbol_id == symbol,
                Order.status == "OPEN"
            )
            .order_by(Order.created_at.asc())
            .all()
        )

    # ----------------------------------------------------------
    # 🔥 (NEW) 주문을 FILLED 로 변경
    # ----------------------------------------------------------
    def mark_filled(self, db, order):
        order.status = "FILLED"
        order.exec_price = order.exec_price or 0  # 또는 이미 처리된 값 사용
        order.filled_qty = order.qty  # 전체 체결
        db.commit()
        db.refresh(order)
        return order

