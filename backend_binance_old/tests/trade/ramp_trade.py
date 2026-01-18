# backend_binance_old/tests/trade/ramp_trade.py
import asyncio

from backend_binance_old.tests.trade.flood_trade import flood

TPS_STEPS = [200, 500, 1000, 1500, 2000]
DURATION = 5  # seconds


async def ramp_test():
    for tps in TPS_STEPS:
        print(f"\n🔥 Ramp Test: {tps} TPS")
        await flood(tps=tps, duration=DURATION)
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(ramp_test())
