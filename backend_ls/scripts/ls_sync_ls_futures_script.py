from backend_ls.app.db.ls_db import SessionLocal
from backend_ls.app.ls_api.tr_3101 import call_3101
from backend_ls.app.ls_api.tr_3105 import call_3105
from backend_ls.app.services.ls_futures_raw_3101_service import LSFuturesRaw3101Service
from backend_ls.app.services.ls_futures_raw_3105_service import LSFuturesRaw3105Service


def run():
    db = SessionLocal()
    try:
        print("▶ 3101 CALL")
        out_3101 = call_3101()
        print(f"3101 rows = {len(out_3101)}")

        LSFuturesRaw3101Service.upsert_from_3101(db, out_3101)

        symbols = [row["Symbol"] for row in out_3101]

        print(symbols)

        print("▶ 3105 CALL")
        out_3105 = call_3105('HSIG26')

        cnt_3105 = LSFuturesRaw3105Service.upsert_from_3105(db, out_3105)

        print(f"3105 rows = {len(out_3105)}")
        print(f"3105 UPSERT = {cnt_3105}")

        print("✅ SYNC DONE")


    finally:
        db.close()


if __name__ == "__main__":
    run()
