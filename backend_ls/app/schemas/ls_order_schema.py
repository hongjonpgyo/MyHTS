from pydantic import BaseModel, field_validator
from typing import Literal, Optional, List

class OrderCreate(BaseModel):
    account_id: str           # 계좌번호
    symbol: str               # HSIF26

    side: Literal["BUY", "SELL"]
    order_type: Literal["LIMIT", "MARKET"]

    qty: int
    request_price: Optional[float] = None

    source: Literal["ORDERBOOK", "SIM", "API"] = "ORDERBOOK"

    # ==========================
    # Validators
    # ==========================
    @field_validator("qty")
    @classmethod
    def validate_qty(cls, v: int):
        if v <= 0:
            raise ValueError("qty must be greater than 0")
        return v

    @field_validator("request_price")
    @classmethod
    def validate_request_price(cls, v: Optional[float], info):
        order_type = info.data.get("order_type")

        # LIMIT: request_price 필수
        if order_type == "LIMIT":
            if v is None or v <= 0:
                raise ValueError("LIMIT 주문은 request_price가 필수입니다")

        # MARKET: request_price 금지
        if order_type == "MARKET":
            if v is not None:
                raise ValueError("MARKET 주문에는 request_price를 보내면 안 됩니다")

        return v

class OrderOut(BaseModel):
    order_id: int

    account_id: str
    symbol: str

    side: str
    order_type: str

    qty: int
    request_price: Optional[float]
    exec_price: Optional[float]

    status: str
    source: str

    class Config:
        from_attributes = True

class OrderCancelRequest(BaseModel):
    order_ids: List[int]

class OrderCancelResponse(BaseModel):
    ok: bool
    cancelled: List[int]

class OrderResponse(BaseModel):
    order_id: int
    account_id: int
    symbol: str
    side: str
    order_type: str
    qty: int
    request_price: float | None
    status: str

    class Config:
        from_attributes = True   # ⭐ 핵심

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
