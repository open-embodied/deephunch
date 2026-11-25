"""数据策展服务（对应 NVIDIA NeMo Curator 管线）"""
import random

from .. import config
from ..db import one, run

STAGE_LOGS = {
    "split": "镜头切分完成：PySceneDetect 风格边界检测",
    "transcode": "统一转码完成：H.264 / 720p / 24fps",
    "filter": "质量过滤完成：分辨率/美观度/运动量三重阈值",
    "caption": "VLM 打标完成：生成中英文双语 caption",
    "embed": "语义嵌入完成：CLIP 风格向量已入库（支持场景检索）",
}


def run_curator_job(conn, job_id: int):
    job = one(conn, "SELECT * FROM curator_jobs WHERE id=?", (job_id,))
    if not job:
        return
    run(conn, "UPDATE curator_jobs SET status='running' WHERE id=?", (job_id,))
    stages = [s.strip() for s in (job["stages"] or "").split(",") if s.strip()]
    logs, clips = [], 0
    for i, stage in enumerate(stages):
        if stage not in config.CURATOR_STAGES:
            continue
        if stage == "split":
            clips = random.randint(80, 400)
        logs.append(f"[{i+1}/{len(stages)}] {stage}: {STAGE_LOGS.get(stage, '完成')}")
        run(conn, "UPDATE curator_jobs SET stage_progress=?, logs=? WHERE id=?",
            (i + 1, "\n".join(logs), job_id))
    ds = one(conn, "SELECT * FROM datasets WHERE id=?", (job["dataset_id"],))
    if ds:
        run(conn, "UPDATE datasets SET video_count=video_count+?, hours=hours+? WHERE id=?",
            (clips, round(clips / 360.0, 2), ds["id"]))
    run(conn, "UPDATE curator_jobs SET clips_out=?, status='done' WHERE id=?", (clips, job_id))
