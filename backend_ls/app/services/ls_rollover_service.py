from datetime import date

from backend_ls.app.repositories.ls_futures_master_repo import LSFuturesMasterRepository

ROLLOVER_DAYS = 7


class LSRolloverService:

    @staticmethod
    def get_active_with_rollover(db, base_code: str):
        today = date.today()

        masters = LSFuturesMasterRepository.get_all_by_base(
            db=db,
            base_code=base_code
        )

        if not masters:
            return {
                "base_code": base_code,
                "active": None,
                "next": None,
                "rollover": False
            }

        # 만기순 정렬
        masters.sort(key=lambda x: x.expiry_date)

        active = masters[0]
        next_contract = masters[1] if len(masters) > 1 else None

        days_left = (active.expiry_date - today).days

        rollover = days_left <= ROLLOVER_DAYS

        return {
            "base_code": base_code,
            "active": {
                "symbol": active.symbol,
                "expiry_date": active.expiry_date,
                "days_left": days_left
            },
            "next": (
                {
                    "symbol": next_contract.symbol,
                    "expiry_date": next_contract.expiry_date,
                    "days_left": (next_contract.expiry_date - today).days
                }
                if rollover and next_contract
                else None
            ),
            "rollover": rollover
        }
