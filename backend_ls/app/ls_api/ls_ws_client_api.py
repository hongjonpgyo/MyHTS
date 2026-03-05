# backend_ls/app/ls_api/ls_ws_client_api.py
import json
import threading
import time
import traceback

import websocket

from backend_ls.app.adapters.ls_tick_adapter import ls_ovc_to_tick
from backend_ls.app.cache.ls_orderbook_cache import ls_orderbook_cache
from backend_ls.app.cache.ls_price_cache import ls_price_cache
from backend_ls.app.cache.symbol_meta_cache import symbol_meta_cache
from backend_ls.app.core.ls_tick_queue_engine import ls_tick_queue_engine
from backend_ls.app.ls_api.ls_auth_api import LSTokenManager
from backend_ls.app.realtime.price_broadcast import PriceBroadcaster
from backend_ls.app.services.ls_auth_service import ls_auth_service
from backend_ls.app.core.ls_config_core import LS_WS_URL


class LSWebSocketClient:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.subscribed = set()
        self.current_ovc_symbol: str | None = None
        self.current_ovh_symbol: str | None = None

        self._stop = False
        self._thread = None

    # ----------------------------
    # symbol utils
    # ----------------------------
    @staticmethod
    def _normalize_symbol(symbol: str | None) -> str:
        return (symbol or "").strip().upper()

    @staticmethod
    def _pad_tr_key(key: str, length: int = 8) -> str:
        # WS TR_KEY는 고정 길이로 공백 패딩이 필요함
        return (key or "").ljust(length)[:length]

    @staticmethod
    def _safe_int(v, default: int = 0) -> int:
        if v in (None, "", " "):
            return default
        try:
            return int(str(v).strip())
        except Exception:
            return default

    @staticmethod
    def _safe_float(v, default: float | None = None) -> float | None:
        if v in (None, "", " "):
            return default
        try:
            return float(str(v).strip())
        except Exception:
            return default

    # ----------------------------
    # lifecycle
    # ----------------------------
    def start(self):
        if self._thread and self._thread.is_alive():
            print("[LS WS] already running")
            return

        self._stop = False
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def run(self):
        while not self._stop:
            try:
                # 토큰 유효성 보장
                if not LSTokenManager.get_token():
                    print("[LS WS] token missing → relogin")
                    ls_auth_service.login()

                print("[LS WS] connecting...")
                self._connect_once()

            except Exception as e:
                print("[LS WS] run error:", e)
                traceback.print_exc()

            # 재연결 대기
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

    def close(self):
        self.stop()

    # ----------------------------
    # websocket callbacks
    # ----------------------------
    def on_open(self, ws):
        self.connected = True
        print("[LS WS] Connected")

        # reconnect 후 재구독
        for tr_cd, tr_key in self.subscribed:
            self._send_subscribe(tr_cd, tr_key)

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            header = data.get("header", {})
            body = data.get("body")

            # ACK는 무시
            if body is None:
                return

            self.handle_realtime_data(header, body)

        except Exception as e:
            print("[LS WS ERROR]", e)
            traceback.print_exc()

    def on_error(self, ws, error):
        self.connected = False
        print("[LS WS] Error:", error)

    def on_close(self, ws, code, msg):
        self.connected = False
        print("[LS WS] Closed", code, msg)

    # ----------------------------
    # connect
    # ----------------------------
    def _connect_once(self):
        self.ws = websocket.WebSocketApp(
            LS_WS_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        # ping/pong 유지
        self.ws.run_forever(
            sslopt={"cert_reqs": 0},
            ping_interval=30,
            ping_timeout=10,
        )

    # ----------------------------
    # realtime handler
    # ----------------------------
    def handle_realtime_data(self, header, body):
        tr_cd = header.get("tr_cd")

        # =====================================================
        # OVC (체결 / 현재가)
        # =====================================================
        if tr_cd == "OVC":
            tick = ls_ovc_to_tick(body)

            if not tick.price or tick.price <= 0:
                return

            symbol = self._normalize_symbol(tick.symbol)
            if not symbol:
                return

            # ✅ tick_size 보장: 없으면 normalize 하지 않음(안전)
            tick_size = symbol_meta_cache.tick_size(symbol)
            if tick_size and tick_size > 0:
                tick.price = ls_price_cache.normalize_price(symbol, tick.price)

            # 캐시에 저장
            tick.symbol = symbol  # 🔥 캐시/엔진 키 통일
            ls_price_cache.update_tick(tick)

            # 예약/전략/DB 처리는 엔진(Worker)로 넘김
            self.on_price_tick(tick)

            # publish
            PriceBroadcaster.publish(
                symbol=symbol,
                price=float(tick.price),
                change_rate=float(tick.change_rate or 0),
                source="LS:OVC",
            )

        # =====================================================
        # OVH (오더북)
        # =====================================================
        elif tr_cd == "OVH":
            # WS에서 body.symbol이 공백 패딩으로 올 수 있음
            raw_symbol = body.get("symbol") or self.current_ovh_symbol
            symbol = self._normalize_symbol(raw_symbol)
            if not symbol:
                return

            bids, asks = self._parse_ovh_orderbook(body, depth=5)

            # ✅ OVH는 거래소가 이미 tick 단위로 준 값이므로 "정규화 금지"
            # (여기서 normalize 하면 0.25 종목이 1.0로 뭉개져서 몇 줄만 남는 현상 발생)

            if bids or asks:
                last_price = ls_price_cache.get_last_price(symbol)
                tick_size = symbol_meta_cache.tick_size(symbol)

                # last_price는 tick 기준으로 정규화(표시 안정용)
                if last_price and tick_size and tick_size > 0:
                    last_price = ls_price_cache.normalize_price(symbol, last_price)

                PriceBroadcaster.publish_orderbook(
                    symbol=symbol,
                    bids=bids,
                    asks=asks,
                    price=last_price,
                    tick_size=tick_size,
                    source="LS:OVH",
                )

                # cache도 같이 업데이트(원하면 UI에서 pull도 가능)
                ls_orderbook_cache.update(
                    symbol=symbol,
                    bids=bids,
                    asks=asks,
                )

    # ----------------------------
    # subscribe helpers
    # ----------------------------
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
        key = self._pad_tr_key(symbol)
        if key == self.current_ovc_symbol:
            return

        self.subscribe("OVC", key)
        self.current_ovc_symbol = key

    def subscribe_watchlist_symbol(self, symbol: str):
        key = self._pad_tr_key(symbol)
        if ("OVC", key) in self.subscribed:
            return
        self.subscribe("OVC", key)

    def set_ovh_symbol(self, symbol: str):
        key = self._pad_tr_key(symbol)
        if key == self.current_ovh_symbol:
            return

        if self.current_ovh_symbol:
            self.unsubscribe("OVH", self.current_ovh_symbol)

        self.subscribe("OVH", key)
        self.current_ovh_symbol = key

    def _send_subscribe(self, tr_cd: str, tr_key: str):
        token = LSTokenManager.get_token()
        msg = {
            "header": {"token": token, "tr_type": "3"},
            "body": {"tr_cd": tr_cd, "tr_key": tr_key},
        }
        self.ws.send(json.dumps(msg))
        print(f"[LS WS] Subscribe sent {tr_cd} {repr(tr_key)}")

    # ----------------------------
    # tick engine hook (non-blocking)
    # ----------------------------
    @staticmethod
    def on_price_tick(tick):
        symbol = (tick.symbol or "").strip().upper()
        if not symbol:
            return

        ls_tick_queue_engine.enqueue_tick(
            symbol=symbol,
            price=float(tick.price),
        )

    # ----------------------------
    # OVH parser
    # ----------------------------
    def _parse_ovh_orderbook(self, body: dict, depth: int = 5):
        bids: list[dict] = []
        asks: list[dict] = []

        for i in range(1, depth + 1):
            ask_p = self._safe_float(body.get(f"offerho{i}"))
            ask_q = self._safe_int(body.get(f"offerrem{i}"), 0)
            ask_c = self._safe_int(body.get(f"offerno{i}"), 0)

            if ask_p is not None and ask_q is not None:
                asks.append({"price": ask_p, "qty": ask_q, "cnt": ask_c})

            bid_p = self._safe_float(body.get(f"bidho{i}"))
            bid_q = self._safe_int(body.get(f"bidrem{i}"), 0)
            bid_c = self._safe_int(body.get(f"bidno{i}"), 0)

            if bid_p is not None and bid_q is not None:
                bids.append({"price": bid_p, "qty": bid_q, "cnt": bid_c})

        # 정렬 안정화(혹시라도 서버가 순서를 바꾸면)
        asks.sort(key=lambda x: x["price"], reverse=True)  # 높은 매도호가부터
        bids.sort(key=lambda x: x["price"], reverse=True)  # 높은 매수호가부터

        return bids, asks