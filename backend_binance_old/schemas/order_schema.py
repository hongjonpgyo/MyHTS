from pydantic import BaseModel
from typing import Optional


class OrderCreate(BaseModel):
    account_id: int
    symbol: str
    side: str
    qty: float
    order_type: str = "MARKET"


class OrderResponse(BaseModel):
    order_id: int
    exec_price: float
    status: str

class LimitOrderRequest(BaseModel):
    account_id: int
    symbol: str
    side: str     # BUY or SELL
    qty: float
    price: float  # 지정가

class OpenOrdersRequest(BaseModel):
    account_id: int

class Config:
    orm_mode = True
