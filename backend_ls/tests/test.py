#1. from backend_ls.app.ls_api.auth import get_access_token
#
# print(get_access_token())

#2. from backend_ls.app.ls_api.futures_master import fetch_futures_master
#
# raw = fetch_futures_master("CME")
#
# items = raw["o3101OutBlock"]
#
# print(items)

from backend_ls.app.ls_api.ls_ws_client import LSWebSocketClient
import time

ws = LSWebSocketClient()
ws.connect()

print("WS client started")

# 🔥 이게 핵심
while True:
    print("WS Live")
    time.sleep(1)


