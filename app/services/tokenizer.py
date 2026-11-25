"""Tokenizer 服务（对应 Cosmos Tokenizer：连续/离散双配置）"""
from .. import config
from ..db import one, run


def run_tokenize_job(conn, job_id: int):
    job = one(conn, "SELECT * FROM tokenize_jobs WHERE id=?", (job_id,))
    if not job:
        return
    run(conn, "UPDATE tokenize_jobs SET status='running' WHERE id=?", (job_id,))
    cfg = config.TOKENIZER_CONFIGS.get(job["tokenizer"])
    if not cfg:
        run(conn, "UPDATE tokenize_jobs SET status='failed' WHERE id=?", (job_id,))
        return
    clips = job["clips_in"] or 1
    if cfg["mode"] == "continuous":
        tokens = clips * 121 // cfg["temporal_stride"] * (720 // cfg["spatial_stride"][0]) ** 2
        compression = f"时间 {cfg['temporal_stride']}x × 空间 {cfg['spatial_stride'][0]}x{cfg['spatial_stride'][1]}"
    else:
        tokens = clips * 49 // cfg["temporal_stride"] * (720 // cfg["spatial_stride"][0]) ** 2
        compression = f"时间 {cfg['temporal_stride']}x × 空间 {cfg['spatial_stride'][0]}x{cfg['spatial_stride'][1]} × 词表 {cfg['codebook_size']}"
    run(conn, "UPDATE tokenize_jobs SET tokens_out=?, compression=?, status='done' WHERE id=?",
        (f"{tokens:,} tokens", compression, job_id))
