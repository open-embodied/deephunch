"""Tokenizer 路由（对应 Cosmos Tokenizer）"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import config
from ..db import get_db, q, run
from ..services import worker

router = APIRouter(prefix="/api/tokenizer", tags=["tokenizer"])


class TokenizeIn(BaseModel):
    dataset_id: int
    tokenizer: str
    direction: str = "encode"
    clips_in: int = 100


@router.get("/configs")
def list_configs():
    return config.TOKENIZER_CONFIGS


@router.post("/jobs")
def create_job(body: TokenizeIn, conn=Depends(get_db)):
    if body.tokenizer not in config.TOKENIZER_CONFIGS:
        raise HTTPException(400, "未知 tokenizer 配置")
    jid = run(conn, "INSERT INTO tokenize_jobs(dataset_id,tokenizer,direction,clips_in,created_at) VALUES(?,?,?,?,datetime('now'))",
              (body.dataset_id, body.tokenizer, body.direction, body.clips_in))
    worker.submit("tokenize", jid)
    return {"id": jid, "status": "queued"}


@router.get("/jobs")
def list_jobs(conn=Depends(get_db)):
    return q(conn, "SELECT * FROM tokenize_jobs ORDER BY id DESC LIMIT 50")
