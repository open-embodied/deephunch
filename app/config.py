"""deephunch 平台全局配置（对应 Cosmos 平台组件开关）"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.environ.get("DEEPHUNCH_DB", os.path.join(DATA_DIR, "deephunch.db"))
ARTIFACT_DIR = os.path.join(DATA_DIR, "artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# ---- 世界模型推理后端（对应 Cosmos Predict / Transfer）----
# mock   : 无 GPU 演示后端，跑通全流程
# remote : 任意 HTTP 推理服务（如本地 Cosmos-Predict2 / 自研扩散模型）
WFM_BACKEND = os.environ.get("DEEPHUNCH_WFM_BACKEND", "mock")
WFM_REMOTE_URL = os.environ.get("DEEPHUNCH_WFM_REMOTE_URL", "")
WFM_REMOTE_TOKEN = os.environ.get("DEEPHUNCH_WFM_REMOTE_TOKEN", "")

# ---- Tokenizer 配置（对应 Cosmos Tokenizer）----
TOKENIZER_CONFIGS = {
    "dh-tok-c8x8x8": {          # 连续 tokenizer：时间8x 空间8x8x（对应 CV8x8x8，供扩散 WFM）
        "mode": "continuous", "temporal_stride": 8, "spatial_stride": (8, 8),
        "max_frames": 121, "latent_channels": 16,
    },
    "dh-tok-d8x16x16": {        # 离散 tokenizer：时间8x 空间16x16（对应 CV8x16x16，供自回归 WFM）
        "mode": "discrete", "temporal_stride": 8, "spatial_stride": (16, 16),
        "max_frames": 49, "codebook_size": 65536,
    },
}

# ---- 数据策展管线（对应 NeMo Curator）----
CURATOR_STAGES = [
    "split",        # 镜头切分
    "transcode",    # 统一转码 (H.264 / 720p / 24fps)
    "filter",       # 分辨率/美观度/运动量过滤
    "caption",      # VLM 打标
    "embed",        # 语义嵌入（视频检索用）
]

# ---- 安全护栏（对应 Cosmos Guardrails 双层架构）----
PRE_GUARD_KEYWORDS = [
    "暴力", "血腥", "色情", "枪支", "爆炸物",
    "violence", "gore", "nsfw", "weapon", "explosive",
]
POST_GUARD_ENABLED = True  # 输出视频审核（人脸模糊占位 + 分类审核）

# ---- 后训练（对应 NeMo 微调）----
POSTTRAIN_PRESETS = {
    "dh-predict-lora": {"method": "lora", "rank": 32, "lr": 1e-4, "epochs": 20},
    "dh-predict-sft": {"method": "sft", "lr": 5e-5, "epochs": 10},
}
