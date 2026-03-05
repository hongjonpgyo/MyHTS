from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend_ls.app.core.admin_auth import get_current_admin
from backend_ls.app.db.ls_db import get_db
from backend_ls.app.models.admin_user_model import AdminUser
from backend_ls.app.models.ls_futures_position_model import Position
from backend_ls.app.models.ls_futures_account_balance_model import LSAccountBalance
from backend_ls.app.core.security import verify_password
from backend_ls.app.core.jwt import create_access_token  # 우리가 만들 것
from backend_ls.app.schemas.admin_account_schema import AdminAccountResponse
from backend_ls.app.cache.ls_price_cache import ls_price_cache

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login")
def admin_login(payload: dict, db: Session = Depends(get_db)):

    user = db.query(AdminUser).filter(
        AdminUser.username == payload["username"]
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload["password"], user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive admin")

    token = create_access_token({"sub": user.username, "role": user.role})

    return {"access_token": token}

@router.get("/accounts", response_model=list[AdminAccountResponse])
def get_accounts(admin=Depends(get_current_admin), db: Session = Depends(get_db)):

    accounts = db.query(LSAccountBalance).all()
    results = []

    for acc in accounts:

        positions = db.query(Position).filter(
            Position.account_id == acc.id
        ).all()

        unrealized = 0
        used_margin = 0

        for pos in positions:
            if pos.qty == 0:
                continue

            last_price = ls_price_cache.get_last_price(pos.symbol)
            if not last_price:
                continue

            unrealized += (last_price - pos.entry_price) * pos.qty * pos.multiplier

            used_margin += abs(pos.qty) * pos.margin_per_contract

        balance = acc.balance + unrealized
        available = balance - used_margin

        if balance > 0:
            risk_ratio = (used_margin / balance) * 100
        else:
            risk_ratio = 100

        if risk_ratio >= 80:
            status = "danger"
        elif risk_ratio >= 50:
            status = "warning"
        else:
            status = "normal"

        results.append(
            AdminAccountResponse(
                account_id=acc.id,
                balance=balance,
                available=available,
                unrealized_pnl=unrealized,
                used_margin=used_margin,
                risk_ratio=round(risk_ratio, 2),
                status=status
            )
        )

    return results