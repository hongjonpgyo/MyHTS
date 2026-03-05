from pydantic import BaseModel


class AdminAccountResponse(BaseModel):
    account_id: int
    balance: float
    available: float
    unrealized_pnl: float
    used_margin: float
    risk_ratio: float
    status: str