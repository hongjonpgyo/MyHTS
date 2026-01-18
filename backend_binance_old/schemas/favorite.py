# schemas/favorite.py
from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    symbol_code: str


class FavoriteOut(BaseModel):
    symbol_code: str

    class Config:
        orm_mode = True
