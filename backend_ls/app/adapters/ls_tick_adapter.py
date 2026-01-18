# backend_ls/app/adapters/ls_tick_adapter.py
from backend_ls.app.models.ls_futures_market_tick import MarketTick


def ls_ovc_to_tick(body: dict) -> MarketTick:
    def f(v):
        return float(v) if v not in (None, "", " ") else None

    def i(v):
        return int(v) if v not in (None, "", " ") else None

    return MarketTick(
        symbol=body.get("symbol"),
        price=f(body.get("curpr")),
        open=f(body.get("open")),
        high=f(body.get("high")),
        low=f(body.get("low")),

        volume=i(body.get("totq")),
        trade_qty=i(body.get("trdq")),

        change=f(body.get("ydiffpr")),
        change_rate=f(body.get("chgrate")),

        trade_time=body.get("kortm"),
        trade_date=body.get("kordate"),

        seq=i(body.get("lSeq")),

        source="LS",
        raw=body,
    )
