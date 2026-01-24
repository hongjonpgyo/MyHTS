from pydantic import BaseModel, field_validator
from typing import Literal, Optional, List


# =====================================================
# Protection (TP / SL)
# =====================================================

ProtectionType = Literal["TP", "SL"]


class ProtectionLeg(BaseModel):
    """
    개별 보호 주문 (TP or SL)
    """
    type: ProtectionType
    price: float
    qty: int

    # --------------------------
    # Validators
    # --------------------------
    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float):
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v

    @field_validator("qty")
    @classmethod
    def validate_qty(cls, v: int):
        if v <= 0:
            raise ValueError("qty must be greater than 0")
        return v


class ProtectionCreate(BaseModel):
    """
    포지션 보호 생성 요청
    """
    account_id: int
    symbol: str

    # 현재 포지션 방향 (검증용)
    side: Literal["LONG", "SHORT"]

    # linked_position_id: Optional[int] = None

    protections: List[ProtectionLeg]

    source: Literal["UI", "API"] = "UI"

    # --------------------------
    # Validators
    # --------------------------
    @field_validator("protections")
    @classmethod
    def validate_protections(cls, v: List[ProtectionLeg]):
        if not v:
            raise ValueError("protections must not be empty")

        # TP / SL 중복 방지
        types = [p.type for p in v]
        if len(types) != len(set(types)):
            raise ValueError("TP / SL type duplicated")

        return v


class ProtectionOut(BaseModel):
    """
    보호 주문 응답 (DB 기반)
    """
    protection_id: int

    account_id: int
    symbol: str
    side: str

    type: ProtectionType
    price: float
    qty: int

    status: str        # WAITING / TRIGGERED / CANCELLED
    source: str

    class Config:
        from_attributes = True   # ⭐ SQLAlchemy 연동 핵심

class ProtectionCancelRequest(BaseModel):
    account_id: int
    symbol: str