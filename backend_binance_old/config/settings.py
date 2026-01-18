# Client configuration

REST_URL = "http://127.0.0.1:9000"
WS_URL = "ws://127.0.0.1:9000/ws"
DEFAULT_SYMBOL = "BTCUSDT"
ORDERBOOK_DEPTH = 100
PRICE_TOLERANCE = 0.5
MATCHING_INTERVAL = 0.1 #100ms
POLLING_INTERVAL = 1
SYMBOLS_LIST = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "NQ",
    "MNQ",
]
BINANCE_DEPTH_URL = "https://api.binance.com/api/v3/depth"
SECRET_KEY = "CHANGE_ME_SECRET"  # TODO: 환경변수/설정에서 가져오도록 변경 권장
ALGORITHM = "HS256"
SYMBOL_META = {
    "NQ": {
        "tick": 0.25,
        "multiplier": 20,
    },
    "MNQ": {
        "tick": 0.25,
        "multiplier": 2,
    },
}



