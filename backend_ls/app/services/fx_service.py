# backend/services/fx_service.py
from backend_ls.app.core import global_rates


class FXService:
    _rates: dict[str, float] = {}

    @classmethod
    def get_rate(currency: str) -> float | None:
        return global_rates.FX_RATES.get(currency)

    @classmethod
    def get_all(cls) -> dict[str, float]:
        return global_rates.FX_RATES
