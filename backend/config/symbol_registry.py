from backend.config.symbols import SymbolType

SYMBOL_REGISTRY = {
    # -----------------
    # Crypto (Binance)
    # -----------------
    "BTCUSDT": {
        "type": SymbolType.CRYPTO,
        "price_source": "binance",
        "tick": 0.1,
        "multiplier": 1,
    },
    "ETHUSDT": {
        "type": SymbolType.CRYPTO,
        "price_source": "binance",
        "tick": 0.01,
        "multiplier": 1,
    },
    "SOLUSDT": {
        "type": SymbolType.CRYPTO,
        "price_source": "binance",
        "tick": 0.01,
        "multiplier": 1,
    },
    # -----------------
    # Futures (CME)
    # -----------------
    "MNQ": {
        "type": SymbolType.FUTURES,
        "price_source": "yahoo",
        "yahoo_symbol": "MNQ=F",
        "tick": 0.25,
        "multiplier": 2,
    },
    "NQ": {
        "type": SymbolType.FUTURES,
        "price_source": "yahoo",
        "yahoo_symbol": "NQ=F",
        "tick": 0.25,
        "multiplier": 20,
    },
}
