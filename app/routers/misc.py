"""安全护栏与模型仓库路由"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..db import get_db, q, run
from ..services import guardrails

router = APIRouter(prefix="/api", tags=["guardrails", "registry"])


class PreGuardIn(BaseModel):
    prompt: str


@router.post("/guardrails/pre")
def pre_check(body: PreGuardIn, conn=Depends(get_db)):
    return guardrails.pre_guard(conn, body.prompt)


@router.get("/guardrails/events")
def events(conn=Depends(get_db)):
    return q(conn, "SELECT * FROM guardrail_events ORDER BY id DESC LIMIT 50")


class ArtifactIn(BaseModel):
    name: str
    family: str = "predict"          # predict / transfer / reason
    size_b: float = 2.0
    version: str = "1.0"
    license: str = "dh-open-model-license"
    uri: str = ""
    notes: str = ""


@router.get("/registry")
def list_artifacts(conn=Depends(get_db)):
    return q(conn, "SELECT * FROM model_artifacts ORDER BY id DESC")


@router.post("/registry")
def add_artifact(body: ArtifactIn, conn=Depends(get_db)):
    new_id = run(conn, "INSERT INTO model_artifacts(name,family,size_b,version,license,uri,notes,created_at) VALUES(?,?,?,?,?,?,?,datetime('now'))",
                 (body.name, body.family, body.size_b, body.version, body.license, body.uri, body.notes))
    return {"id": new_id, "name": body.name}
