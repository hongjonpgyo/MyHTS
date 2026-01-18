# backend_ls/app/schemas/ls_futures_position_model.py
from pydantic import BaseModel

class PositionOut(BaseModel):
    account_id: str
    symbol: str
    qty: float
    side: str

    avg_price: float
    last_price: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float

    class Config:
        from_attributes = True
