import time
import threading
import yfinance as yf


class YahooPriceThread(threading.Thread):
    def __init__(self, cache, symbol: str, yahoo_symbol: str, interval_sec: float = 1.0):
        super().__init__(daemon=True)
        self.cache = cache
        self.symbol = symbol.upper()            # 내부 심볼 (예: "NQ", "MNQ")
        self.yahoo_symbol = yahoo_symbol        # 야후 심볼 (예: "^NDX", "NQ=F" 등)
        self.interval_sec = interval_sec

        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        # ticker 객체는 루프 밖에서 1번만 생성하는게 좋아(매번 만들면 무거움)
        ticker = yf.Ticker(self.yahoo_symbol)

        while not self._stop_event.is_set():
            try:
                fi = getattr(ticker, "fast_info", None) or {}

                # 안전하게 last_price 얻기
                price = fi.get("last_price") or fi.get("lastPrice")
                if price is None:
                    # fast_info가 비면 history fallback (조금 느리지만 안전)
                    hist = ticker.history(period="1d", interval="1m")
                    if not hist.empty:
                        price = float(hist["Close"].iloc[-1])

                if price is not None:
                    p = float(price)
                    # ✅ MarketCache는 update() 사용
                    self.cache.update(self.symbol, bid=p, ask=p, last=p)
                else:
                    print(f"[FUTURES PRICE] no price: {self.yahoo_symbol}")

            except Exception as e:
                print("[FUTURES PRICE ERROR]", e)

            # stop 이벤트를 더 빨리 반영하도록 작은 sleep 조각으로 쪼갤 수도 있음
            self._stop_event.wait(self.interval_sec)
