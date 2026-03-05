# backend_ls/app/schemas/ls_futures_position_model.py
from pydantic import BaseModel
from typing import Literal, Optional

class PositionOut(BaseModel):
    account_id: int
    symbol: str
    qty: float
    side: str

    avg_price: float
    last_price: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    liquidation_price: Optional[float]

    class Config:
        from_attributes = True

class ClosePositionRequest(BaseModel):
    account_id: int
    symbol: str
    source: Literal["UI", "API", "SIM"] = "UI"

class ClosePositionResponse(BaseModel):
    ok: bool
    account_id: int
    symbol: str
    closed_side: Optional[str] = None       # BUY/SELL
    closed_qty: Optional[float] = None
    cancelled_reservations: int = 0
    deactivated_protections: int = 0
    created_order_id: Optional[int] = None
    reason: Optional[str] = None
