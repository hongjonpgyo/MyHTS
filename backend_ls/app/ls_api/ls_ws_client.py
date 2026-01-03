# backend_ls/app/ls_api/ls_ws_client.py
import json
import threading
import websocket

from backend_ls.app.cache.price_cache import price_cache
from backend_ls.app.ls_api.auth import get_access_token
from backend_ls.app.core.config import LS_WS_URL

class LSWebSocketClient:
    def __init__(self):
        self.ws = None
        self.connected = False
    # -------------------------------------------------
    # WS OPEN
    # -------------------------------------------------
    def on_open(self, ws):
        self.connected = True
        print("[LS WS] Connected")
        self.subscribe()

    # -------------------------------------------------
    # WS MESSAGE
    # -------------------------------------------------
    def on_message(self, ws, message):
        data = json.loads(message)

        header = data.get("header", {})
        body = data.get("body")

        if body is None:
            print(f"[LS WS] ACK {header.get('tr_cd')}")
            return

        self.handle_realtime_data(header, body)

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
        print("[LS WS] Error:", error)

    def on_close(self, ws, code, msg):
        self.connected = False
        print("[LS WS] Closed", code, msg)

    # -------------------------------------------------
    # CONNECT
    # -------------------------------------------------
    def connect(self):
        self.ws = websocket.WebSocketApp(
            LS_WS_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        t = threading.Thread(
            target=self.ws.run_forever,
            kwargs={"sslopt": {"cert_reqs": 0}},
            daemon=True
        )
        t.start()

    def handle_realtime_data(self, header, body):
        tr_cd = header.get("tr_cd")

        if tr_cd == "OVH":
            symbol = body.get("symbol")
            price = self._to_float(body.get("price"))

            if not symbol or price is None:
                return

            price_cache.update(
                symbol=symbol,
                price=price,
                raw=body
            )

            print(f"[CACHE] {symbol} = {price}")

    def subscribe(self):
        token = get_access_token()

        msg = {
            "header": {
                "token": token,
                "tr_type": "3"
            },
            "body": {
                "tr_cd": "OVH",
                "tr_key": "HSIF26"
            }
        }

        self.ws.send(json.dumps(msg))
        print("[LS WS] Subscribe OVH sent")

