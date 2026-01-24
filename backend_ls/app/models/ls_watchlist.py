from dataclasses import dataclass
from typing import Optional

@dataclass
class LSWatchlistRow:
    symbol: str
    name: str
    last_price: Optional[float] = None
    change: Optional[float] = None
