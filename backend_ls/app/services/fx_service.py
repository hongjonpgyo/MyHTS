# backend/services/fx_service.py
from decimal import Decimal

from backend_ls.app.core import global_rates


class FXService:
    _rates: dict[str, float] = {}

    # @classmethod
    # def get_rate(currency: str) -> float | None:
    #     return global_rates.FX_RATES.get(currency)

    @classmethod
    def get_all(cls) -> dict[str, float]:
        return global_rates.FX_RATES

    @classmethod
    def get_rate(cls, currency: str) -> Decimal:
        rate = global_rates.FX_RATES.get(currency)
        if not rate:
            return Decimal("1")
        return Decimal(str(rate))
