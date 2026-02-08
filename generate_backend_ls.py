# generate_backend_ls.py
import os

BASE_DIR = "backend_ls" #sync test000

DIRS = [
    "app",
    "app/core",
    "app/ls_api",
    "app/routers",
    "app/services",
    "app/repositories",
    "tests",
]

FILES = [
    "app/main.py",
    "app/__init__.py",

    "app/core/ls_config_core.py",
    "app/core/logging_core.py",
    "app/core/security.py",
    "app/core/__init__.py",

    "app/ls_api/ls_auth_service.py",
    "app/ls_api/ls_futures_master_api.py",
    "app/ls_api/price.py",
    "app/ls_api/__init__.py",

    "app/routers/health.py",
    "app/routers/ls_futures_router.py",
    "app/routers/__init__.py",

    "app/services/ls_futures_master_service.py",
    "app/services/price_service.py",
    "app/services/__init__.py",

    "app/repositories/ls_futures_symbol_repository.py",
    "app/repositories/__init__.py",

    "tests/__init__.py",

    ".env",
    "requirements.txt",
    "README.md",
]


def create_dirs():
    for d in DIRS:
        path = os.path.join(BASE_DIR, d)
        os.makedirs(path, exist_ok=True)


def create_files():
    for f in FILES:
        path = os.path.join(BASE_DIR, f)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fp:
                if f.endswith("main.py"):
                    fp.write("""from fastapi import FastAPI

app = FastAPI(title="LS OpenAPI Backend")

@app.get("/")
def root():
    return {"status": "ok"}
""")
                elif f.endswith("README.md"):
                    fp.write("# LS OpenAPI Backend\n\nLS 증권 OpenAPI 전용 백엔드\n")
                else:
                    fp.write("")


def main():
    print("📦 Creating backend_ls structure...")
    os.makedirs(BASE_DIR, exist_ok=True)
    create_dirs()
    create_files()
    print("✅ backend_ls structure created successfully!")


if __name__ == "__main__":
    main()
