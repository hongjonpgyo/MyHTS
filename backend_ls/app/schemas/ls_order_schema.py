from pydantic import BaseModel, field_validator
from typing import Literal, Optional, List

# ==========================
# Create
# ==========================
class OrderCreate(BaseModel):
    account_id: int
    symbol: str
    side: Literal["BUY", "SELL"]
    order_type: Literal["LIMIT", "MARKET"]
    qty: int
    request_price: float | None = None
    source: Literal["ORDERBOOK", "SIM", "API"] = "ORDERBOOK"

    @field_validator("qty")
    def validate_qty(cls, v):
        if v <= 0:
            raise ValueError("qty must be greater than 0")
        return v

    @field_validator("request_price")
    def validate_request_price(cls, v, info):
        order_type = info.data.get("order_type")
        if order_type == "LIMIT" and (v is None or v <= 0):
            raise ValueError("LIMIT 주문은 request_price가 필수입니다")
        if order_type == "MARKET" and v is not None:
            raise ValueError("MARKET 주문에는 request_price를 보내면 안 됩니다")
        return v


# ==========================
# Response
# ==========================
class OrderResponse(BaseModel):
    order_id: int
    account_id: int
    symbol: str
    side: str
    order_type: str
    qty: int
    request_price: float | None
    exec_price: float | None
    status: str
    source: str

    class Config:
        from_attributes = True


# ==========================
# Cancel
# ==========================
class OrderCancelRequest(BaseModel):
    order_ids: List[int]

class OrderCancelResponse(BaseModel):
    ok: bool
    cancelled: List[int]

