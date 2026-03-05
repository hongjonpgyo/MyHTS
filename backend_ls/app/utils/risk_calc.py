from decimal import Decimal, InvalidOperation


def calc_liquidation_price(
    deposit_krw: Decimal,
    maintenance_margin_krw: Decimal,
    avg_price: Decimal,
    qty: Decimal,                 # LONG:+, SHORT:-
    multiplier: Decimal,          # e.g. HSI=50 (HKD)
    fx_rate: Decimal,             # HKD->KRW, e.g. 182.08
) -> Decimal | None:
    """
    liquidation condition: deposit + unrealized == maintenance_margin
    unrealized = (liq - avg) * qty * multiplier * fx_rate
    """
    try:
        if qty == 0:
            return None
        if fx_rate <= 0 or multiplier <= 0:
            return None

        target_unrealized = maintenance_margin_krw - deposit_krw  # usually negative
        denom = qty * multiplier * fx_rate

        # liq_price = avg_price + target_unrealized / denom
        liq_price = avg_price + (target_unrealized / denom)

        # 가격은 음수가 될 수 없으니 방어
        if liq_price <= 0:
            return None

        return liq_price

    except (InvalidOperation, ZeroDivisionError):
        return None