# backend_binance_old/tests/chaos/run_chaos_test.py
import asyncio
import random
from chaos_client import ChaosTradeClient

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
CLIENTS = 15
DURATION = 30  # seconds

async def main():
    clients = []

    for i in range(CLIENTS):
        sym = random.choice(SYMBOLS)
        c = ChaosTradeClient(f"C{i}", sym)
        clients.append(c)

    tasks = []
    for c in clients:
        tasks.append(asyncio.create_task(c.run()))
        tasks.append(asyncio.create_task(c.chaos()))

    print("🔥 CHAOS TEST START")
    await asyncio.sleep(DURATION)

    for c in clients:
        c.running = False
        await c.disconnect()

    print("\n📊 CHAOS RESULT")
    total_recv = 0
    total_reconnect = 0

    for c in clients:
        print(
            f"{c.name} [{c.symbol}] recv={c.received} reconnect={c.reconnects}"
        )
        total_recv += c.received
        total_reconnect += c.reconnects

    print("\n🔥 TOTAL")
    print("Trades received:", total_recv)
    print("Reconnects:", total_reconnect)

if __name__ == "__main__":
    asyncio.run(main())
