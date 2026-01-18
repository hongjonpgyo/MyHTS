from pydantic import BaseModel
from typing import Optional


class AccountCreate(BaseModel):
    user_id: int


class AccountResponse(BaseModel):
    account_id: int
    user_id: int
    balance: float
    pnl_realized: float
    pnl_unrealized: float

    class Config:
        orm_mode = True
