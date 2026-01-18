import asyncio
import json
import ssl
import websockets

BINANCE_WS_URL = "wss://stream.binance.com:9443"


class MarketStream:
    def __init__(self, market_cache):
        self.market_cache = market_cache
        self.symbols = []
        self.ws = None
        self.is_running = False

    def add_symbol(self, symbol: str):
        s = symbol.lower()
        if s not in self.symbols:
            self.symbols.append(s)

    async def connect(self):
        if not self.symbols:
            print("⚠️ 등록된 심볼 없음")
            return

        stream_list = []
        for s in self.symbols:
            stream_list.append(f"{s}@bookTicker")       # best bid/ask
            stream_list.append(f"{s}@ticker")           # last + stats
            stream_list.append(f"{s}@depth20@100ms")    # depth

        streams = "/".join(stream_list)
        url = f"{BINANCE_WS_URL}/stream?streams={streams}"
        print("📡 Binance Connect →", url)

        ssl_context = ssl._create_unverified_context()
        self.is_running = True

        while self.is_running:
            try:
                async with websockets.connect(
                    url,
                    ssl=ssl_context,
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:
                    self.ws = ws
                    print("✅ Binance WS 연결 성공!")

                    async for msg in ws:
                        self.handle_message(msg)

            except Exception as e:
                print("🚨 Binance WS 오류:", e)
                await asyncio.sleep(3)

    def handle_message(self, msg: str):
        try:
            root = json.loads(msg)
            stream = root.get("stream", "")
            d = root.get("data")
            if not stream or not isinstance(d, dict):
                return

            symbol = stream.split("@")[0].upper()

            # 1) bookTicker: { "b": "...", "a": "..." }
            if "@bookTicker" in stream:
                bid = d.get("b")
                ask = d.get("a")
                if bid is None or ask is None:
                    return
                self.market_cache.upsert_price(symbol, bid=float(bid), ask=float(ask))
                return

            # 2) ticker: last("c")가 핵심
            if "@ticker" in stream:
                last = d.get("c") or d.get("lastPrice")
                if last is None:
                    return
                self.market_cache.upsert_price(symbol, last=float(last))
                return

            # 3) depth: { "bids":[[p,q]..], "asks":[[p,q]..] }
            if "@depth" in stream:
                bids_raw = d.get("bids", [])
                asks_raw = d.get("asks", [])
                if not bids_raw or not asks_raw:
                    return

                bids = [(float(p), float(q)) for p, q in bids_raw]
                asks = [(float(p), float(q)) for p, q in asks_raw]

                self.market_cache.update_depth(symbol, bids=bids, asks=asks)
                return

        except Exception as e:
            print("⚠️ WS message 처리 오류:", e)
