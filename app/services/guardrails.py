"""安全护栏服务（对应 Cosmos Guardrails 双层架构：Pre-guard + Post-guard）"""
from .. import config
from ..db import run


def pre_guard(conn, prompt: str) -> dict:
    """Pre-guard：提示词关键词拦截（生产环境可换接 Aegis 类内容安全模型）"""
    low = prompt.lower()
    for kw in config.PRE_GUARD_KEYWORDS:
        if kw in low:
            run(conn, "INSERT INTO guardrail_events(phase,action,reason,created_at) VALUES('pre','block',?,datetime('now'))",
                (f"命中关键词: {kw}",))
            return {"allowed": False, "reason": f"提示词命中禁用关键词「{kw}」"}
    run(conn, "INSERT INTO guardrail_events(phase,action,reason,created_at) VALUES('pre','pass','通过',datetime('now'))")
    return {"allowed": True, "reason": "通过"}


def post_guard(conn, artifact: str) -> dict:
    """Post-guard：输出审核（生产环境接视频分类模型 + 人脸模糊；此处为占位）"""
    action = "blur" if config.POST_GUARD_ENABLED else "pass"
    run(conn, "INSERT INTO guardrail_events(phase,action,reason,created_at) VALUES('post',?,'输出审核完成（占位：建议人脸模糊/NSFW 分类）',datetime('now'))",
        (action,))
    return {"artifact": artifact, "action": action}
