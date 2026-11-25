"""数据策展路由（对应 NeMo Curator）"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..db import get_db, one, q, run
from ..services import worker

router = APIRouter(prefix="/api/curator", tags=["curator"])


class DatasetIn(BaseModel):
    name: str
    domain: str = "robotics"
    license: str = "proprietary"


class CuratorIn(BaseModel):
    dataset_id: int
    source_uri: str
    stages: str = "split,transcode,filter,caption,embed"


@router.get("/datasets")
def list_datasets(conn=Depends(get_db)):
    return q(conn, "SELECT * FROM datasets ORDER BY id DESC")


@router.post("/datasets")
def create_dataset(body: DatasetIn, conn=Depends(get_db)):
    if one(conn, "SELECT id FROM datasets WHERE name=?", (body.name,)):
        raise HTTPException(400, "数据集名称已存在")
    new_id = run(conn, "INSERT INTO datasets(name,domain,license,created_at) VALUES(?,?,?,datetime('now'))",
                 (body.name, body.domain, body.license))
    return {"id": new_id, "name": body.name}


@router.post("/jobs")
def create_job(body: CuratorIn, conn=Depends(get_db)):
    if not one(conn, "SELECT id FROM datasets WHERE id=?", (body.dataset_id,)):
        raise HTTPException(404, "数据集不存在")
    jid = run(conn, "INSERT INTO curator_jobs(dataset_id,source_uri,stages,created_at) VALUES(?,?,?,datetime('now'))",
              (body.dataset_id, body.source_uri, body.stages))
    worker.submit("curator", jid)
    return {"id": jid, "status": "queued"}


@router.get("/jobs")
def list_jobs(conn=Depends(get_db)):
    return q(conn, "SELECT * FROM curator_jobs ORDER BY id DESC LIMIT 50")


@router.get("/jobs/{job_id}")
def get_job(job_id: int, conn=Depends(get_db)):
    job = one(conn, "SELECT * FROM curator_jobs WHERE id=?", (job_id,))
    if not job:
        raise HTTPException(404, "任务不存在")
    return job
