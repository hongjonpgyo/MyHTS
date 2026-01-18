# backend_ls/app/schemas/ls_account_schema.py

from pydantic import BaseModel

class AccountBalanceOut(BaseModel):
    account_id: int

    deposit: float              # 예탁금
    available: float            # 가용예탁금
    unrealized_pnl: float       # 평가손익
    unrealized_pnl_rate: float  # 평가손익률 (%)

    class Config:
        from_attributes = True
