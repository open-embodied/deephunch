"""后训练服务（对应 NeMo 微调：LoRA / SFT）"""
import json
import random

from .. import config
from ..db import one, run


def build_config(job: dict) -> dict:
    preset = config.POSTTRAIN_PRESETS.get(job["preset"], {})
    return {
        "base_model": job["base_model"],
        "method": preset.get("method", "lora"),
        "lora_rank": preset.get("rank"),
        "learning_rate": preset.get("lr", 1e-4),
        "epochs": preset.get("epochs", 10),
        "dataset_id": job["dataset_id"],
        "precision": "bf16",
        "output": f"artifacts/posttrain_{job['id']}/",
    }


def run_posttrain_job(conn, job_id: int):
    job = one(conn, "SELECT * FROM posttrain_jobs WHERE id=?", (job_id,))
    if not job:
        return
    run(conn, "UPDATE posttrain_jobs SET status='running' WHERE id=?", (job_id,))
    cfg = build_config(job)
    run(conn, "UPDATE posttrain_jobs SET config_json=? WHERE id=?",
        (json.dumps(cfg, ensure_ascii=False), job_id))
    loss = 0.9
    for ep in range(1, cfg["epochs"] + 1):
        loss *= random.uniform(0.88, 0.97)  # mock 训练曲线
        run(conn, "UPDATE posttrain_jobs SET epoch=?, loss=? WHERE id=?",
            (ep, round(loss, 4), job_id))
    run(conn, "UPDATE posttrain_jobs SET artifact=?, status='done' WHERE id=?",
        (f"artifacts/posttrain_{job_id}/lora_final.safetensors", job_id))
