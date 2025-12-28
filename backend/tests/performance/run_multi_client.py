# backend/tests/trade/run_multi_client.py
import asyncio
from backend.tests.performance.multi_client import TradeClient

async def main():
    clients = [
        TradeClient("C1", "BTCUSDT", 500, 10),
        TradeClient("C2", "ETHUSDT", 300, 10),
        TradeClient("C3", "SOLUSDT", 700, 10),
        TradeClient("C4", "BTCUSDT", 1000, 10),
    ]

    tasks = [asyncio.create_task(c.run()) for c in clients]

    results = await asyncio.gather(*tasks)
    print("🔥 TOTAL trades:", sum(results))

if __name__ == "__main__":
    asyncio.run(main())
