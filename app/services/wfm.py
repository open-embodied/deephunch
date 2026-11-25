"""世界模型生成服务（对应 Cosmos Predict / Transfer，可插拔后端）"""
import json
import os
import random

from .. import config
from ..db import one, run


def _mock_artifact(job: dict) -> str:
    out = {
        "job_id": job["id"], "type": job["job_type"], "model": job["model"],
        "prompt": job["prompt"], "seed": job["seed"], "duration_s": job["duration_s"],
        "note": "mock 后端产物；接入真实后端后此处为 mp4 视频文件",
    }
    path = os.path.join(config.ARTIFACT_DIR, f"gen_{job['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return path


def _remote_artifact(job: dict) -> str:
    import httpx
    payload = {
        "model": job["model"], "mode": job["job_type"], "prompt": job["prompt"],
        "seed": job["seed"], "duration_s": job["duration_s"],
    }
    headers = {"Authorization": f"Bearer {config.WFM_REMOTE_TOKEN}"} if config.WFM_REMOTE_TOKEN else {}
    r = httpx.post(f"{config.WFM_REMOTE_URL.rstrip('/')}/generate", json=payload, headers=headers, timeout=600)
    r.raise_for_status()
    video_url = r.json().get("video_url", "")
    if video_url.startswith("http"):
        path = os.path.join(config.ARTIFACT_DIR, f"gen_{job['id']}.mp4")
        with httpx.stream("GET", video_url, timeout=600) as resp, open(path, "wb") as f:
            for chunk in resp.iter_bytes():
                f.write(chunk)
        return path
    return video_url


def run_gen_job(conn, job_id: int):
    job = one(conn, "SELECT * FROM gen_jobs WHERE id=?", (job_id,))
    if not job:
        return
    run(conn, "UPDATE gen_jobs SET status='running', backend=? WHERE id=?",
        (config.WFM_BACKEND, job_id))
    try:
        if config.WFM_BACKEND == "remote" and config.WFM_REMOTE_URL:
            artifact = _remote_artifact(job)
        else:
            artifact = _mock_artifact(job)
        run(conn, "UPDATE gen_jobs SET artifact=?, status='done' WHERE id=?", (artifact, job_id))
    except Exception as e:  # noqa: BLE001
        run(conn, "UPDATE gen_jobs SET artifact=?, status='failed' WHERE id=?",
            (f"error: {e}", job_id))


def estimate_cost(model: str, duration_s: int) -> dict:
    """生成成本估算（供商业化模块使用）"""
    unit = {"dh-predict-2b": 0.8, "dh-predict-8b": 2.5, "dh-transfer-2b": 1.2}.get(model, 1.0)
    return {"gpu_seconds_est": int(duration_s * unit * random.uniform(8, 12)), "model": model}
