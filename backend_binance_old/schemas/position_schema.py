from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PositionBase(BaseModel):
    account_id: int
    symbol_id: int
    qty: float
    entry_price: Optional[float] = None
    realized_pnl: float = 0.0


class PositionResponse(PositionBase):
    position_id: int
    updated_at: datetime

    class Config:
        orm_mode = True
