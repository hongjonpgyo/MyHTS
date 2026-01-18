from datetime import datetime

from pydantic import BaseModel
from typing import Literal, Optional

class ReservationCreate(BaseModel):
    account_id: int
    symbol: str

    side: Literal["BUY", "SELL"]
    qty: float

    trigger_op: Literal[">=", "<="]
    trigger_price: float

    order_type: Literal["LIMIT", "MARKET"]
    request_price: Optional[float] = None  # LIMIT일 때만

    linked_position_id: Optional[int] = None

class ReservationOut(BaseModel):
    reservation_id: int
    account_id: int
    symbol: str
    side: str
    qty: int

    trigger_price: float
    trigger_op: str

    order_type: str
    request_price: float | None

    status: str

    created_at: datetime
    triggered_at: datetime | None

    class Config:
        from_attributes = True  # pydantic v2
