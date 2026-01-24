from backend_ls.app.models.ls_futures_protection_model import LSFuturesProtection
from backend_ls.app.models.ls_reservation_model import OrderReservation
from backend_ls.app.repositories.ls_futures_protection_repo import protection_repo
from backend_ls.app.repositories.ls_futures_reservation_repo import reservation_repo
from backend_ls.app.repositories.ls_futures_watchlist_repo import LSFuturesWatchlistRepository


class LSFuturesService:

    @staticmethod
    def get_watchlist(db, only_has_price: bool, limit: int):
        return LSFuturesWatchlistRepository.fetch_watchlist(
        db,
            only_has_price=only_has_price,
            limit=limit
        )

    @staticmethod
    def create_protections(
        db,
        payload,  # ProtectionCreate
    ):
        created_rows = []

        for leg in payload.protections:
            # -----------------------------
            # 1️⃣ 기존 보호주문 비활성화
            # -----------------------------
            db.query(LSFuturesProtection).filter(
                LSFuturesProtection.account_id == payload.account_id,
                LSFuturesProtection.symbol == payload.symbol,
                LSFuturesProtection.type == leg.type,
                LSFuturesProtection.is_active == True,
            ).update(
                {"is_active": False},
                synchronize_session=False,
            )

            # -----------------------------
            # 2️⃣ 신규 보호주문 생성
            # -----------------------------
            protection = LSFuturesProtection(
                account_id=payload.account_id,
                symbol=payload.symbol,
                side=payload.side,          # LONG / SHORT
                type=leg.type,              # TP / SL
                price=leg.price,
                qty=leg.qty,
                is_active=True,
            )

            db.add(protection)
            db.flush()  # ⭐ protection.id 확보

            # -----------------------------
            # 3️⃣ 보호주문 → 예약주문 변환
            # -----------------------------
            is_long = payload.side == "LONG"

            if leg.type == "TP":
                trigger_op = ">=" if is_long else "<="
                order_side = "SELL" if is_long else "BUY"
            else:  # SL
                trigger_op = "<=" if is_long else ">="
                order_side = "SELL" if is_long else "BUY"

            reservation = OrderReservation(
                account_id=payload.account_id,
                symbol=payload.symbol,

                side=order_side,
                qty=leg.qty,

                trigger_op=trigger_op,
                trigger_price=leg.price,

                order_type="MARKET",        # ⭐ 초기엔 MARKET 고정 추천
                request_price=None,

                # linked_position_id=payload.linked_position_id,
                protection_id=protection.id,  # ⭐ 핵심
                status="WAITING",
            )

            db.add(reservation)

            created_rows.append(protection)

        db.commit()
        return created_rows


    @staticmethod
    def get_protections(
            db,
            account_id: int,
            symbol: str | None = None,
    ):
        query = db.query(LSFuturesProtection).filter(
            LSFuturesProtection.account_id == account_id,
            LSFuturesProtection.is_active == True,
        )

        if symbol:
            query = query.filter(
                LSFuturesProtection.symbol == symbol
            )

        rows = query.order_by(
            LSFuturesProtection.type.asc()
        ).all()

        return [
            {
                "account_id": r.account_id,
                "symbol": r.symbol,
                "side": r.side,
                "type": r.type,
                "price": float(r.price),
                "qty": r.qty,
            }
            for r in rows
        ]

    @staticmethod
    def cancel_protections(db, account_id: int, symbol: str):
        # 보호주문
        protection_repo.deactivate_by_symbol(db, account_id, symbol)

        # 예약
        reservation_repo.cancel_waiting_by_symbol(db, account_id, symbol)


