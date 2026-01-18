from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SymbolBase(BaseModel):
    symbol_code: str
    exchange: str
    tick_size: float
    tick_value: float
    multiplier: float
    initial_margin: Optional[float] = None
    maintenance_margin: Optional[float] = None
    expiration_date: Optional[datetime] = None


class SymbolCreate(SymbolBase):
    pass


class SymbolResponse(SymbolBase):
    symbol_id: int
    created_at: datetime

    class Config:
        orm_mode = True
