import os
from pathlib import Path

BASE = Path("backend")

# 폴더 목록
folders = [
    BASE / "api",
    BASE / "services",
    BASE / "services" / "market",
    BASE / "repositories",
    BASE / "schemas",
    BASE / "db",
    BASE / "core",
    BASE / "utils",
]

# 파일 목록
files = {
    BASE / "main.py": "",
    # API
    BASE / "api" / "accounts_api.py": "",
    BASE / "api" / "orders_api.py": "",
    BASE / "api" / "positions_api.py": "",
    BASE / "api" / "executions_api.py": "",
    BASE / "api" / "symbols_api.py": "",
    BASE / "api" / "market_api.py": "",

    # Services
    BASE / "services" / "account_service.py": "",
    BASE / "services" / "order_service.py": "",
    BASE / "services" / "position_service.py": "",
    BASE / "services" / "execution_service.py": "",
    BASE / "services" / "risk_service.py": "",

    # Market (추가)
    BASE / "services" / "market" / "ls_market_cache.py.20251208": "",
    BASE / "services" / "market" / "market_stream.py.20251208": "",
    BASE / "services" / "market" / "market_service.py": "",

    # Repositories
    BASE / "repositories" / "account_repo.py": "",
    BASE / "repositories" / "order_repo.py": "",
    BASE / "repositories" / "position_repo.py": "",
    BASE / "repositories" / "execution_repo.py": "",
    BASE / "repositories" / "symbol_repo.py": "",

    # Schemas
    BASE / "schemas" / "account_schema.py": "",
    BASE / "schemas" / "order_schema.py": "",
    BASE / "schemas" / "position_schema.py": "",
    BASE / "schemas" / "execution_schema.py": "",
    BASE / "schemas" / "symbol_schema.py": "",
    BASE / "schemas" / "market_schema.py": "",

    # DB
    BASE / "db" / "ls_database.py": "",
    BASE / "db" / "models.py": "",

    # Core
    BASE / "core" / "ls_config.py": "",
    BASE / "core" / "security.py": "",

    # Utils
    BASE / "utils" / "pnl_calculator.py": "",
    BASE / "utils" / "margin_calculator.py": "",
    BASE / "utils" / "price_fetcher.py": "",
}


def create_structure():
    print("📁 Creating full FastAPI backend structure with MarketDataService...\n")

    # 폴더 생성
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"[DIR] {folder}")

    # 파일 생성
    for filepath, content in files.items():
        if not filepath.exists():
            filepath.write_text(content, encoding="utf-8")
            print(f"[FILE] {filepath}")
        else:
            print(f"[SKIP] {filepath}")

    print("\n🎉 Backend folder structure created successfully!")


if __name__ == "__main__":
    create_structure()
