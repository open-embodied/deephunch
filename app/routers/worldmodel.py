"""世界模型生成路由（对应 Cosmos Predict / Transfer）"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..db import get_db, q, run
from ..services import guardrails, wfm, worker

router = APIRouter(prefix="/api/worldmodel", tags=["worldmodel"])


class GenIn(BaseModel):
    job_type: str = "text2world"      # text2world / image2world / video2world / transfer
    prompt: str
    model: str = "dh-predict-2b"
    seed: int = 0
    duration_s: int = 5


@router.post("/jobs")
def create_job(body: GenIn, conn=Depends(get_db)):
    # Pre-guard 安全护栏
    check = guardrails.pre_guard(conn, body.prompt)
    if not check["allowed"]:
        return {"blocked": True, **check}
    jid = run(conn, "INSERT INTO gen_jobs(job_type,prompt,model,seed,duration_s,created_at) VALUES(?,?,?,?,?,datetime('now'))",
              (body.job_type, body.prompt, body.model, body.seed, body.duration_s))
    worker.submit("generate", jid)
    return {"blocked": False, "id": jid, "status": "queued"}


@router.get("/jobs")
def list_jobs(conn=Depends(get_db)):
    return q(conn, "SELECT * FROM gen_jobs ORDER BY id DESC LIMIT 50")


@router.post("/estimate")
def estimate(body: GenIn):
    return wfm.estimate_cost(body.model, body.duration_s)
