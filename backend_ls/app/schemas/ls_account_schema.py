# backend_ls/app/schemas/ls_account_schema.py

from pydantic import BaseModel

class AccountBalanceOut(BaseModel):
    account_id: int

    deposit: float              # 예탁금
    used_margin: float          # 사용증거금 🔥 추가
    available: float            # 가용예탁금
    unrealized_pnl: float       # 평가손익
    unrealized_pnl_rate: float  # 평가손익률 (%)
    equity: float               # 계좌평가 🔥 추가

    class Config:
        from_attributes = True