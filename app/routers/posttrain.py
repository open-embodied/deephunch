"""后训练路由（对应 NeMo 微调）"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..db import get_db, one, q, run
from ..services import worker

router = APIRouter(prefix="/api/posttrain", tags=["posttrain"])


class PosttrainIn(BaseModel):
    base_model: str = "dh-predict-2b"
    preset: str = "dh-predict-lora"
    dataset_id: int


@router.post("/jobs")
def create_job(body: PosttrainIn, conn=Depends(get_db)):
    jid = run(conn, "INSERT INTO posttrain_jobs(base_model,preset,dataset_id,created_at) VALUES(?,?,?,datetime('now'))",
              (body.base_model, body.preset, body.dataset_id))
    worker.submit("posttrain", jid)
    return {"id": jid, "status": "queued"}


@router.get("/jobs")
def list_jobs(conn=Depends(get_db)):
    return q(conn, "SELECT * FROM posttrain_jobs ORDER BY id DESC LIMIT 50")


@router.get("/jobs/{job_id}")
def get_job(job_id: int, conn=Depends(get_db)):
    job = one(conn, "SELECT * FROM posttrain_jobs WHERE id=?", (job_id,))
    if not job:
        raise HTTPException(404, "任务不存在")
    return job
