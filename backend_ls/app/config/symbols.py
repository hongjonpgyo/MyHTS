from dataclasses import dataclass

@dataclass(frozen=True)
class LSSymbolConfig:
    symbol: str        # 내부 심볼 (HSIF26)
    name: str          # 한글명 (항셍F26)
    exchange: str      # 거래소
    tick_size: float
    price_source: str  # ls / binance / mock

# WATCHLIST_SOURCE = "config"
WATCHLIST_SOURCE = "DB"

LSSYMBOLS = [
    # SymbolConfig("CUSF26", "위안F26", "CME", 0.01, "ls"),
    # SymbolConfig("CUSG26", "위안G26", "CME", 0.01, "ls"),
    # SymbolConfig("CUSH26", "위안H26", "CME", 0.01, "ls"),
    # SymbolConfig("CUSZ26", "위안Z26", "CME", 0.01, "ls"),
    #
    # SymbolConfig("HCEIF26", "항셍중국F26", "HKEX", 1, "ls"),
    # SymbolConfig("HCEIG26", "항셍중국G26", "HKEX", 1, "ls"),
    # SymbolConfig("HCEIH26", "항셍중국H26", "HKEX", 1, "ls"),

    LSSymbolConfig("HSIF26", "항셍F26", "HKEX", 1, "ls"),
    # SymbolConfig("HCHHG26", "항셍G26", "HKEX", 1, "ls"),
    # SymbolConfig("HCHHH26", "항셍H26", "HKEX", 1, "ls"),
]
