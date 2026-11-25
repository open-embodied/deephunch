"""演示数据初始化：创建示例数据集与模型工件
用法：python scripts/init_demo.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import q, run, session

if __name__ == "__main__":
    with session() as conn:
        if not q(conn, "SELECT id FROM datasets LIMIT 1"):
            run(conn, "INSERT INTO datasets(name,domain,license,created_at) VALUES('demo-warehouse-humanoid','robotics','internal',datetime('now'))")
            run(conn, "INSERT INTO datasets(name,domain,license,created_at) VALUES('demo-parking-av','av','internal',datetime('now'))")
        if not q(conn, "SELECT id FROM model_artifacts LIMIT 1"):
            rows = [
                ("dh-predict-2b", "predict", 2.0, "统一 Text2World/Image2World/Video2World 基础模型"),
                ("dh-predict-8b", "predict", 8.0, "高质量长序列世界模型"),
                ("dh-transfer-2b", "transfer", 2.0, "sim2real 结构控制视频翻译（ControlNet 架构）"),
                ("dh-reason-2b", "reason", 2.0, "物理 AI 推理 VLM，支持 2D/3D 定位与长上下文"),
            ]
            for name, family, size, notes in rows:
                run(conn, "INSERT INTO model_artifacts(name,family,size_b,notes,created_at) VALUES(?,?,?,?,datetime('now'))",
                    (name, family, size, notes))
    print("演示数据初始化完成")
