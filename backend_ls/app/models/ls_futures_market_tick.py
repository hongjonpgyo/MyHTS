# backend_ls/app/models/ls_futures_market_tick.py
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class MarketTick:
    symbol: str                  # HSIF26
    price: float                 # 현재가
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None

    volume: Optional[int] = None         # 누적 거래량
    trade_qty: Optional[int] = None      # 틱 거래량

    change: Optional[float] = None       # 전일 대비
    change_rate: Optional[float] = None  # 등락률 %

    trade_time: Optional[str] = None     # HHMMSS (한국시간)
    trade_date: Optional[str] = None     # YYYYMMDD

    seq: Optional[int] = None             # lSeq (실시간 순번)

    source: str = "LS"                    # LS / BINANCE / etc
    raw: Optional[Dict[str, Any]] = None  # 원본 데이터
