# backend_binance_old/scripts/generate_cqg_mock.py
import os
from pathlib import Path

BASE_DIR = Path("backend_binance_old/services/market/cqg")


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str):
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"✅ created: {path}")


def main():
    ensure_dir(BASE_DIR)

    # -------------------------------------------------
    # __init__.py
    # -------------------------------------------------
    write_file(
        BASE_DIR / "__init__.py",
        """
from .base import CQGAdapter
from .mock_adapter import MockCQGAdapter
        """
    )

    # -------------------------------------------------
    # ls_futures_base_model.py
    # -------------------------------------------------
    write_file(
        BASE_DIR / "ls_futures_base_model.py",
        """
from abc import ABC, abstractmethod
from typing import Callable


class CQGAdapter(ABC):
    \"\"\"
    CQG / Mock 공통 인터페이스
    \"\"\"

    def __init__(self):
        self.on_price: Callable = lambda data: None
        self.on_trade: Callable = lambda data: None

    def set_price_handler(self, handler: Callable):
        self.on_price = handler

    def set_trade_handler(self, handler: Callable):
        self.on_trade = handler

    @abstractmethod
    def subscribe(self, symbol: str):
        ...

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...
        """
    )

    # -------------------------------------------------
    # mock_adapter.py
    # -------------------------------------------------
    write_file(
        BASE_DIR / "mock_adapter.py",
        """
import time
import random
import threading

from .base import CQGAdapter


class MockCQGAdapter(CQGAdapter):
    \"\"\"
    CQG Mock Adapter
    - CME futures 느낌의 가격 움직임
    - tick size: 0.25
    \"\"\"

    def __init__(self, base_price: float = 16000.0):
        super().__init__()
        self.price = base_price
        self.running = False
        self.symbols = []

    def subscribe(self, symbol: str):
        if symbol not in self.symbols:
            self.symbols.append(symbol)

    def start(self):
        if self.running:
            return
        self.running = True
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        print("🚀 Mock CQG Adapter started")

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            delta = random.choice([-1, 1]) * random.uniform(0, 1)
            self.price += delta

            # CME tick snap
            last = round(round(self.price / 0.25) * 0.25, 2)
            bid = last - 0.25
            ask = last + 0.25

            ts = time.time()

            # 🔹 Price update
            self.on_price({
                "symbol": "NQ",
                "bid": bid,
                "ask": ask,
                "last": last,
                "ts": ts,
            })

            # 🔹 Trade event (확률적)
            if random.random() < 0.4:
                self.on_trade({
                    "symbol": "NQ",
                    "price": last,
                    "qty": random.choice([1, 2]),
                    "side": random.choice(["BUY", "SELL"]),
                    "ts": ts,
                })

            time.sleep(0.2)
        """
    )

    print("\\n🎉 CQG Mock 구조 생성 완료!")


if __name__ == "__main__":
    main()
