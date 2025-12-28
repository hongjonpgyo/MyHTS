from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TESTS_DIR = BASE_DIR / "tests"

STRUCTURE = {
    "__init__.py": "",
    "README.md": """# Backend Test Suite

## trade/
- flood_trade.py : 대량 체결 발생 테스트
- ws_consumer.py : WS 수신 테스트
- trade_latency_test.py : 체결 지연 측정

## performance/
- queue_pressure.py : asyncio.Queue 압력 테스트
- multi_client.py : 다중 WS 클라이언트 테스트

## manual/
- playground.py : 실험용 임시 코드
""",
    "trade": {
        "__init__.py": "",
        "flood_trade.py": """# 대량 체결 발생 테스트
if __name__ == "__main__":
    print("Run flood_trade test")
""",
        "ws_consumer.py": """# WS 수신 테스트
if __name__ == "__main__":
    print("Run ws_consumer test")
""",
        "trade_latency_test.py": """# Trade latency 측정
if __name__ == "__main__":
    print("Run trade_latency_test")
""",
    },
    "performance": {
        "__init__.py": "",
        "queue_pressure.py": """# Queue 압력 테스트
if __name__ == "__main__":
    print("Run queue_pressure test")
""",
        "multi_client.py": """# 다중 WS 클라이언트 테스트
if __name__ == "__main__":
    print("Run multi_client test")
""",
    },
    "manual": {
        "__init__.py": "",
        "playground.py": """# 실험용 임시 코드
if __name__ == "__main__":
    print("Manual playground")
""",
    },
}


def create_structure(base: Path, tree: dict):
    for name, content in tree.items():
        path = base / name

        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(content, encoding="utf-8")
                print(f"Created file: {path}")
            else:
                print(f"Skipped existing file: {path}")


if __name__ == "__main__":
    print("📁 Creating backend/tests structure...")
    TESTS_DIR.mkdir(exist_ok=True)
    create_structure(TESTS_DIR, STRUCTURE)
    print("✅ Done.")
