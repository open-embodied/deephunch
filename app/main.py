"""deephunch 平台入口（FastAPI）"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .db import init_db
from .routers import curator, tokenizer, worldmodel, posttrain, misc

app = FastAPI(title="deephunch", description="物理AI 世界基础模型平台（Cosmos 架构开源复刻）", version="1.0.0")

init_db()
app.include_router(curator.router)
app.include_router(tokenizer.router)
app.include_router(worldmodel.router)
app.include_router(posttrain.router)
app.include_router(misc.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
def health():
    return {"status": "ok", "wfm_backend": config.WFM_BACKEND,
            "tokenizers": list(config.TOKENIZER_CONFIGS.keys())}
