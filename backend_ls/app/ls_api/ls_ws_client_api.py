# backend_ls/app/ls_api/ls_ws_client_api.py
import json
import threading
import time
import traceback

import websocket

from backend_ls.app.adapters.ls_tick_adapter import ls_ovc_to_tick
from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.db.ls_db import SessionLocal
from backend_ls.app.ls_api.ls_auth_api import LSTokenManager
from backend_ls.app.services.ls_auth_service import ls_auth_service
from backend_ls.app.core.ls_config_core import LS_WS_URL
from backend_ls.app.services.ls_market_tick_service import LSMarketTickService

class LSWebSocketClient:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.subscribed = set()
        self.current_ovc_symbol: str | None = None

        self._stop = False
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            print("[LS WS] already running")
            return

        self._stop = False
        self._thread = threading.Thread(
            target=self.run,
            daemon=True
        )
        self._thread.start()

    def run(self):
        while not self._stop:
            try:
                # 🔥 토큰 유효성 보장
                if not LSTokenManager.get_token():
                    print("[LS WS] token missing → relogin")
                    ls_auth_service.login()

                print("[LS WS] connecting...")
                self._connect_once()

            except Exception as e:
                print("[LS WS] run error:", e)
                traceback.print_exc()

            # 🔁 재연결 대기
            print("[LS WS] retry in 5s")
            for _ in range(5):
                if self._stop:
                    return
                time.sleep(1)

    def stop(self):
        self._stop = True
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass

    @staticmethod
    def _pad_tr_key(key: str, length: int = 8) -> str:
        return (key or "").ljust(length)[:length]

    # -------------------------------------------------
    # WS OPEN
    # -------------------------------------------------
    def on_open(self, ws):
        self.connected = True
        print("[LS WS] Connected")

        for tr_cd, tr_key in self.subscribed:
            self._send_subscribe(tr_cd, tr_key)

    # -------------------------------------------------
    # WS MESSAGE
    # -------------------------------------------------
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            header = data.get("header", {})
            body = data.get("body")

            tr_cd = header.get("tr_cd")
            print(f"🔥 TR_CD = {tr_cd}")

            # ACK는 무시
            if body is None:
                return

            self.handle_realtime_data(header, body)

        except Exception as e:
            print("[LS WS ERROR]", e)
            traceback.print_exc()

    # -------------------------------------------------
    # UTILS
    # -------------------------------------------------
    @staticmethod
    def _to_float(v):
        if v in (None, "", " "):
            return None
        return float(str(v).strip())

    @staticmethod
    def _to_int(v):
        if v in (None, "", " "):
            return None
        return int(str(v).strip())

    # -------------------------------------------------
    # ERROR / CLOSE
    # -------------------------------------------------
    def on_error(self, ws, error):
        self.connected = False
        print("[LS WS] Error:", error)

    def on_close(self, ws, code, msg):
        self.connected = False
        print("[LS WS] Closed", code, msg)


    def close(self):
        self.stop()

    def _connect_once(self):
        self.ws = websocket.WebSocketApp(
            LS_WS_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        self.ws.run_forever(
            sslopt={"cert_reqs": 0},
            ping_interval=30,
            ping_timeout=10,
        )

    def handle_realtime_data(self, header, body):
        tr_cd = header.get("tr_cd")
        print("tr_cd : " + tr_cd)
        if tr_cd == "OVC":
            tick = ls_ovc_to_tick(body)

            # 1️⃣ 가격 캐시 갱신
            ls_price_cache.update_tick(tick)
            print(f"[TICK] {tick.symbol} {tick.price}")

            # 2️⃣ 🔥 체결 시뮬레이터 호출 (핵심)
            self.on_price_tick(tick)

    def subscribe(self, tr_cd: str, tr_key: str):
        key = self._pad_tr_key(tr_key)
        self.subscribed.add((tr_cd, key))

        if self.connected:
            self._send_subscribe(tr_cd, key)

    def unsubscribe(self, tr_cd: str, tr_key: str):
        key = self._pad_tr_key(tr_key)

        if (tr_cd, key) not in self.subscribed:
            return

        token = LSTokenManager.get_token()
        msg = {
            "header": {"token": token, "tr_type": "4"},  # 4 = 해제
            "body": {"tr_cd": tr_cd, "tr_key": key},
        }

        try:
            self.ws.send(json.dumps(msg))
            print(f"[LS WS] Unsubscribe sent {tr_cd} {repr(key)}")
        except Exception:
            pass

        self.subscribed.discard((tr_cd, key))

    def set_ovc_symbol(self, symbol: str):
        symbol = self._pad_tr_key(symbol)

        if symbol == self.current_ovc_symbol:
            return

        # 기존 OVC 해제
        if self.current_ovc_symbol:
            self.unsubscribe("OVC", self.current_ovc_symbol)

        # 신규 OVC 구독
        self.subscribe("OVC", symbol)
        self.current_ovc_symbol = symbol

    def _send_subscribe(self, tr_cd: str, tr_key: str):
        token = LSTokenManager.get_token()
        print(token)
        msg = {
            "header": {"token": token, "tr_type": "3"},
            "body": {"tr_cd": tr_cd, "tr_key": tr_key},
        }
        print('ws send start')
        self.ws.send(json.dumps(msg))

        print(f"[LS WS] Subscribe sent {tr_cd} {repr(tr_key)}")

    @staticmethod
    def on_price_tick(tick):
        db = SessionLocal()
        try:
            symbol = tick.symbol
            if not symbol:
                return

            LSMarketTickService.on_tick(
                db=db,
                symbol=symbol,
                last_price=tick.price,
            )

        finally:
            db.close()



