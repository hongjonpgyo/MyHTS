import threading
import time

from backend_ls.app.db.ls_db import SessionLocal
from backend_ls.app.services.ls_market_tick_service import LSMarketTickService


class LSTickQueueEngine:

    def __init__(self):
        self.buffer = {}
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

    # -------------------------------------------------
    # start worker
    # -------------------------------------------------

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._worker,
            daemon=True
        )

        self.thread.start()

        print("[TICK ENGINE] started")

    # -------------------------------------------------
    # enqueue (overwrite 방식)
    # -------------------------------------------------

    def enqueue_tick(self, symbol: str, price: float):

        if not symbol:
            return

        symbol = symbol.strip().upper()

        with self.lock:
            self.buffer[symbol] = price

    # -------------------------------------------------
    # worker
    # -------------------------------------------------

    def _worker(self):

        db = SessionLocal()

        try:

            while self.running:

                time.sleep(0.05)   # 20Hz

                with self.lock:

                    if not self.buffer:
                        continue

                    items = self.buffer
                    self.buffer = {}

                try:

                    for symbol, price in items.items():

                        LSMarketTickService.on_tick(
                            db=db,
                            symbol=symbol,
                            last_price=price
                        )

                except Exception as e:
                    print("[TICK ENGINE ERROR]", e)

        finally:
            db.close()


# -------------------------------------------------
# singleton
# -------------------------------------------------

ls_tick_queue_engine = LSTickQueueEngine()