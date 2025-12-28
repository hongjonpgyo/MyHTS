# backend/tests/chaos/chaos_client.py
import asyncio
import json
import random
import time
import websockets

class ChaosTradeClient:
    def __init__(self, name, symbol, base_url="ws://127.0.0.1:9000"):
        self.name = name
        self.symbol = symbol.lower()
        self.url = f"{base_url}/ws/trades/{self.symbol}"
        self.running = True
        self.ws = None

        self.received = 0
        self.reconnects = 0

    async def connect(self):
        self.ws = await websockets.connect(self.url)
        print(f"🔌 {self.name} connected ({self.symbol})")

    async def disconnect(self):
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.reconnects += 1
            print(f"❌ {self.name} disconnected")

    async def run(self):
        while self.running:
            try:
                if not self.ws:
                    await self.connect()

                async for msg in self.ws:
                    data = json.loads(msg)
                    self.received += 1

            except Exception:
                await asyncio.sleep(0.1)

    async def chaos(self):
        while self.running:
            await asyncio.sleep(random.uniform(0.5, 2.0))
            await self.disconnect()
            await asyncio.sleep(random.uniform(0.1, 1.0))
