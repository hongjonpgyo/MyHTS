from fastapi import FastAPI
from backend_ls.app.routers.futures import router as sync_symbols
from backend_ls.app.routers.futures import router as sync_master

app = FastAPI(title="LS OpenAPI Backend")

app.include_router(sync_symbols)
app.include_router(sync_master)

@app.get("/")
def root():
    return {"status": "ok"}


