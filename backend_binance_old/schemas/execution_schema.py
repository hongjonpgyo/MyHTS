from pydantic import BaseModel


class ExecutionResponse(BaseModel):
    exec_id: int
    order_id: int
    price: float
    qty: float
    fee: float

    class Config:
        orm_mode = True
