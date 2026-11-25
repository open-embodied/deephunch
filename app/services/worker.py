"""后台任务执行器（线程池，演示用；生产可换 Celery/Arq）"""
from concurrent.futures import ThreadPoolExecutor

from ..db import session
from . import curator, tokenizer, wfm, posttrain

_pool = ThreadPoolExecutor(max_workers=4)

JOBS = {
    "curator": curator.run_curator_job,
    "tokenize": tokenizer.run_tokenize_job,
    "generate": wfm.run_gen_job,
    "posttrain": posttrain.run_posttrain_job,
}


def submit(kind: str, job_id: int):
    fn = JOBS[kind]

    def _run():
        with session() as conn:
            fn(conn, job_id)

    _pool.submit(_run)
