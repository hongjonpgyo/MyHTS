from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.position_model import Position
from backend.models.symbol_model import Symbol  # ← 반드시 정확한 경로로 import
from backend.services.order_service import order_service

#   위치 알려주면 수정해 줄게

router = APIRouter(prefix="/positions", tags=["Positions"])

class CloseAllRequest(BaseModel):
    account_id: int

@router.get("/{account_id}/{symbol_code}")
def get_position(
    account_id: int,
    symbol_code: str,
    db: Session = Depends(get_db),
):
    """
    특정 계좌 + 특정 심볼 포지션 1건 조회
    """
    symbol_code = symbol_code.upper()

    row = (
        db.query(Position, Symbol.symbol_code)
        .join(Symbol, Position.symbol_id == Symbol.symbol_id)
        .filter(
            Position.account_id == account_id,
            Symbol.symbol_code == symbol_code,
        )
        .first()
    )

    if not row:
        return None   # 🔥 프론트에서 None 처리

    pos, symbol_name = row
    qty = float(pos.qty)

    return {
        "position_id": pos.position_id,
        "account_id": pos.account_id,
        "symbol_id": pos.symbol_id,
        "symbol": symbol_name,
        "side": "LONG" if qty >= 0 else "SHORT",
        "qty": qty,
        "entry_price": float(pos.entry_price),
        "unrealized_pnl": float(pos.realized_pnl or 0),
        "updated_at": pos.updated_at.isoformat() if pos.updated_at else None,
    }

@router.get("/{account_id}")
def get_positions(account_id: int, db: Session = Depends(get_db)):
    """
    계좌의 모든 포지션 조회 → symbol 문자열 포함해서 반환
    """
    rows = (
        db.query(Position, Symbol.symbol_code)
        .join(Symbol, Position.symbol_id == Symbol.symbol_id)
        .filter(Position.account_id == account_id)
        .all()
    )

    result = []
    for pos, symbol_name in rows:
        qty = float(pos.qty)

        result.append(
            {
                "position_id": pos.position_id,
                "account_id": pos.account_id,
                "symbol_id": pos.symbol_id,
                "symbol": symbol_name,                      # 🔥 프론트에서 필요한 필드
                "side": "LONG" if qty >= 0 else "SHORT",   # qty로 방향 계산
                "qty": qty,
                "entry_price": float(pos.entry_price),
                "unrealized_pnl": float(pos.realized_pnl or 0),
                "updated_at": pos.updated_at.isoformat() if pos.updated_at else None,
            }
        )

    return result

@router.post("/close_symbol")
def close_symbol(
    account_id: int,
    symbol: str,
    db: Session = Depends(get_db),
):
    pos = (
        db.query(Position)
        .filter(
            Position.account_id == account_id,
            Position.symbol == symbol,
            Position.qty != 0
        )
        .first()
    )

    if not pos:
        return {"ok": True, "message": "no position"}

    qty = float(pos.qty)
    side = "SELL" if qty > 0 else "BUY"

    try:
        order_service.place_market_order(
            db=db,
            account_id=account_id,
            symbol=symbol,
            side=side,
            qty=abs(qty),
            reason="CLOSE_SYMBOL"
        )
    except Exception as e:
        raise HTTPException(400, f"close_symbol failed: {e}")

    return {
        "ok": True,
        "symbol": symbol,
        "closed_qty": abs(qty)
    }

@router.post("/close_all")
def close_all(
    req: CloseAllRequest,
    db: Session = Depends(get_db),
):
    positions = (
        db.query(Position, Symbol.symbol_code)
        .join(Symbol, Position.symbol_id == Symbol.symbol_id)
        .filter(
            Position.account_id == req.account_id,
            Position.qty != 0
        )
        .all()
    )

    if not positions:
        return {"ok": True, "message": "no positions"}

    results = []

    try:
        for pos, symbol_code in positions:
            qty = float(pos.qty)
            side = "SELL" if qty > 0 else "BUY"

            order_service.place_market_order(
                db=db,
                account_id=req.account_id,   # ✅
                symbol_code=symbol_code,          # ✅
                side=side,
                qty=abs(qty),
                # reason="CLOSE_ALL"
            )

            results.append({
                "symbol": symbol_code,
                "qty": abs(qty),
                "side": side
            })

    except Exception as e:
        print("[CLOSE_ALL ERROR DETAIL]", e)
        raise HTTPException(400, f"close_all failed: {e}")

    return {
        "ok": True,
        "closed": results
    }

