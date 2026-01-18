# 1. token get
# from backend_ls.app.ls_api.ls_auth import get_access_token
#
# print(get_access_token())

from backend_ls.app.ls_api.ls_ws_client_api import LSWebSocketClient
import time

ws = LSWebSocketClient()
ws.subscribe("OVC", "HSIF26")

ws.connect()

print("WS client started")

# 🔥 이게 핵심
while True:
    print("WS Live")
    time.sleep(1)


