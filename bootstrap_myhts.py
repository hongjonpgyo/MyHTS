import os
from pathlib import Path
import textwrap

ROOT = Path("MyHTS")

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"[SKIP] {path} already exists")
        return
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"[OK]   {path}")

def main():
    # 1) 기본 디렉토리
    (ROOT / "apps" / "backend_binance_old").mkdir(parents=True, exist_ok=True)
    (ROOT / "apps" / "marketdata").mkdir(parents=True, exist_ok=True)
    (ROOT / "apps" / "engine").mkdir(parents=True, exist_ok=True)
    (ROOT / "apps" / "ui_desktop").mkdir(parents=True, exist_ok=True)
    (ROOT / "shared" / "schemas").mkdir(parents=True, exist_ok=True)

    # 2) requirements.txt
    write(
        ROOT / "requirements.txt",
        """
        fastapi
        uvicorn
        pydantic
        sqlalchemy
        psycopg2-binary
        aiohttp
        websockets
        python-dotenv
        PyQt6
        requests
        """
    )

    # 3) README
    write(
        ROOT / "README.md",
        """
        # MyHTS

        1차 목표: Python 데스크탑 HTS (PyQt6 + FastAPI)
        2차 목표: Web HTS 클라이언트
        3차 목표: Mobile App (Flutter or React Native)

        구조:
        - apps/backend_binance_old      : FastAPI 기반 API 서버
        - apps/ui_desktop   : PyQt6 기반 HTS 클라이언트
        - apps/marketdata   : (추가 예정) 시세/호가 수집 엔진
        - apps/engine       : (추가 예정) 매칭엔진/시뮬레이터
        - shared/schemas    : 공통 Pydantic 모델
        """
    )

    # 4) backend_binance_old: FastAPI 기본 서버
    write(
        ROOT / "apps" / "backend_binance_old" / "main.py",
        """
        from fastapi import FastAPI
        from pydantic import BaseModel
        from typing import List

        app = FastAPI(title="MyHTS Backend", version="0.1.0")

        class OrderRequest(BaseModel):
            user_id: int
            account_id: int
            symbol: str
            side: str          # "BUY" or "SELL"
            qty: float
            order_type: str = "MARKET"  # MARKET / LIMIT
            price: float | None = None

        class OrderResponse(BaseModel):
            ok: bool
            order_id: int | None = None
            message: str | None = None

        @app.get("/health")
        async def health():
            return {"status": "ok", "service": "backend_binance_old"}

        @app.post("/orders", response_model=OrderResponse)
        async def place_order(order: OrderRequest):
            # TODO: 이후 engine / risk / account_service 연동
            fake_order_id = 1
            return OrderResponse(
                ok=True,
                order_id=fake_order_id,
                message="order accepted (stub)"
            )

        @app.get("/ping")
        async def ping():
            return {"msg": "MyHTS backend_binance_old alive"}
        """
    )

    # 5) shared/schemas 예시
    write(
        ROOT / "shared" / "schemas" / "orders.py",
        """
        from pydantic import BaseModel

        class Order(BaseModel):
            id: int | None = None
            user_id: int
            account_id: int
            symbol: str
            side: str            # BUY / SELL
            qty: float
            order_type: str      # MARKET / LIMIT
            price: float | None = None
        """
    )

    # 6) PyQt6 UI 기본 창
    write(
        ROOT / "apps" / "ui_desktop" / "main_window.py",
        r'''
        import sys
        import requests
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QWidget,
            QVBoxLayout, QHBoxLayout, QLabel,
            QPushButton, QLineEdit, QComboBox, QMessageBox
        )

        BACKEND_URL = "http://127.0.0.1:9000"

        class MainWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("MyHTS (Python Desktop v0.1)")
                self.setGeometry(200, 200, 1000, 600)

                central = QWidget()
                self.setCentralWidget(central)
                layout = QVBoxLayout(central)

                # 간단한 헤더
                header = QLabel("MyHTS - Python Desktop HTS (1차 목표)")
                layout.addWidget(header)

                # 심볼 선택 + 매수/매도
                form = QHBoxLayout()
                layout.addLayout(form)

                self.combo_symbol = QComboBox()
                self.combo_symbol.addItems(["BTCUSDT", "ETHUSDT", "XRPUSDT"])
                form.addWidget(QLabel("Symbol:"))
                form.addWidget(self.combo_symbol)

                self.edit_qty = QLineEdit()
                self.edit_qty.setPlaceholderText("Quantity (e.g. 0.001)")
                form.addWidget(QLabel("Qty:"))
                form.addWidget(self.edit_qty)

                self.btn_buy = QPushButton("시장가 매수")
                self.btn_sell = QPushButton("시장가 매도")
                form.addWidget(self.btn_buy)
                form.addWidget(self.btn_sell)

                self.btn_buy.clicked.connect(self.on_buy_market)
                self.btn_sell.clicked.connect(self.on_sell_market)

                # 상태 표시
                self.label_status = QLabel("Backend 상태: 미확인")
                layout.addWidget(self.label_status)

                btn_check = QPushButton("Backend 상태 점검")
                btn_check.clicked.connect(self.check_backend)
                layout.addWidget(btn_check)

            def check_backend(self):
                try:
                    r = requests.get(f"{BACKEND_URL}/health", timeout=2)
                    if r.ok:
                        data = r.json()
                        self.label_status.setText(f"Backend OK: {data}")
                    else:
                        self.label_status.setText("Backend 응답 오류")
                except Exception as e:
                    self.label_status.setText(f"Backend 연결 실패: {e}")

            def _send_order(self, side: str):
                symbol = self.combo_symbol.currentText()
                try:
                    qty = float(self.edit_qty.text())
                except ValueError:
                    QMessageBox.warning(self, "Order", "수량을 숫자로 입력하세요.")
                    return

                payload = {
                    "user_id": 1,
                    "account_id": 1,
                    "symbol": symbol,
                    "side": side,
                    "qty": qty,
                    "order_type": "MARKET",
                    "price": None,
                }
                try:
                    r = requests.post(f"{BACKEND_URL}/orders", json=payload, timeout=3)
                    if not r.ok:
                        QMessageBox.warning(self, "Order", f"주문 실패: {r.status_code}")
                        return
                    data = r.json()
                    if data.get("ok"):
                        QMessageBox.information(self, "Order", f"주문 접수: {data}")
                    else:
                        QMessageBox.warning(self, "Order", f"주문 거절: {data}")
                except Exception as e:
                    QMessageBox.warning(self, "Order", f"서버 오류: {e}")

            def on_buy_market(self):
                self._send_order("BUY")

            def on_sell_market(self):
                self._send_order("SELL")


        if __name__ == "__main__":
            app = QApplication(sys.argv)
            win = MainWindow()
            win.show()
            sys.exit(app.exec())
        '''
    )

    print("\n✅ MyHTS skeleton created. Next steps:")
    print("1) cd MyHTS")
    print("2) python -m venv venv && source venv/bin/activate (또는 Windows 방식)")
    print("3) pip install -r requirements.txt")
    print("4) uvicorn apps.backend_binance_old.main:app --reload --port 9000")
    print("5) python apps/ui_desktop/main_window.py")

if __name__ == "__main__":
    main()
