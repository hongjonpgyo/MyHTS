#1. from backend_ls.app.ls_api.auth import get_access_token
#
# print(get_access_token())

from backend_ls.app.ls_api.futures_master import fetch_futures_master

raw = fetch_futures_master("CME")

items = raw["o3101OutBlock"]

print(items)
