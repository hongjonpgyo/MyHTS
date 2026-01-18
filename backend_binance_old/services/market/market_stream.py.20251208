import asyncio
import json
import websockets
import ssl

BINANCE_WS_URL = "wss://stream.binance.com:9443"


class MarketStream:

    def __init__(self, market_cache):
        self.market_cache = market_cache
        self.symbol_streams = []
        self.ws = None
        self.is_running = False

    def add_symbol(self, symbol: str):
        stream_name = f"{symbol.lower()}@bookTicker"
        self.symbol_streams.append(stream_name)

    async def connect(self):
        """Binance WebSocket 연결 및 메시지 수신"""

        if not self.symbol_streams:
            print("⚠️ 등록된 심볼 없음")
            return

        streams = "/".join(self.symbol_streams)
        url = f"{BINANCE_WS_URL}/stream?streams={streams}"

        print(f"📡 Binance Connect → {url}")

        # ❗ SSL 보안 검증 끄기
        ssl_context = ssl._create_unverified_context()

        self.is_running = True

        while self.is_running:
            try:
                async with websockets.connect(
                    url,
                    ssl=ssl_context,   # ★ 여기가 핵심 해결점 ★
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:

                    self.ws = ws
                    print("✅ Binance WS 연결 성공!")

                    async for msg in ws:
                        self.handle_message(msg)

            except Exception as e:
                print(f"🚨 Binance WS 오류: {e}")
                print("⏳ 3초 후 재접속")
                await asyncio.sleep(3)

    def handle_message(self, msg):
        """bookTicker 메시지를 캐시에 반영"""
        try:
            data = json.loads(msg)
            if "data" not in data:
                return

            t = data["data"]
            symbol = t["s"]
            bid = float(t["b"])
            ask = float(t["a"])
            last = (bid + ask) / 2

            self.market_cache.update(symbol, bid, ask, last)

        except Exception as e:
            print("⚠️ message 처리 오류:", e)
