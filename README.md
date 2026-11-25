# deephunch — 物理AI 世界基础模型平台（Cosmos 架构开源复刻）

> deephunch 是对 NVIDIA Cosmos「世界基础模型平台」的架构级一比一复刻，面向机器人、自动驾驶、具身智能等物理 AI 场景，提供**数据策展 → Tokenization → 世界模型生成 → 后训练 → 安全护栏**的完整闭环平台。

## 平台组成（与 Cosmos 对应）

| 模块 | 对应 Cosmos 组件 | 说明 |
|---|---|---|
| `curator` 数据策展 | NVIDIA NeMo Curator | 视频上传、镜头拆分、GPU/占位转码、质量过滤、打标(caption)、嵌入，输出训练数据集 |
| `tokenizer` 视觉分词 | Cosmos Tokenizer | 连续(CV8x8x8)/离散(CV8x16x16) 双配置，编解码任务与压缩统计 |
| `worldmodel` 世界模型 | Cosmos Predict / Transfer | text2world、image2world、video2world、sim2real(transfer) 生成任务，可插拔后端 |
| `posttrain` 后训练 | NeMo Framework 微调 | LoRA/SFT 微调任务编排，配置生成与任务跟踪 |
| `guardrails` 安全护栏 | Cosmos Guardrails | Pre-guard 提示词过滤 + Post-guard 输出审核双层架构 |
| `registry` 模型仓库 | NGC 模型目录 | 模型工件（checkpoint/LoRA）注册、版本与许可管理 |

## 快速开始

```bash
# 方式一：直接运行
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8300
# 浏览器打开 http://localhost:8300 （中文控制台）

# 方式二：Docker
docker compose up -d --build
```

## 默认生成后端

平台默认使用 `mock` 后端（无需 GPU 即可跑通全流程）；接入真实世界模型时，在
`app/config.py` 中将 `WFM_BACKEND` 指向你的推理服务（如本地部署的
Cosmos-Predict2 / 自研扩散模型服务）即可，任务编排代码无需改动。

## 目录结构

```
deephunch/
├── app/
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 平台配置
│   ├── db.py / models.py  # SQLite 持久化
│   ├── routers/           # curator / tokenizer / worldmodel / posttrain / guardrails / registry
│   ├── services/          # 各域业务逻辑与可插拔后端
│   └── static/index.html  # 中文 Web 控制台
├── docs/                  # 架构与部署文档
├── scripts/init_demo.py   # 演示数据初始化
├── docker-compose.yml
└── requirements.txt
```

## 文档

- [平台架构](docs/architecture.md)
- [部署手册](docs/deploy.md)

## 许可

Apache License 2.0。本项目为教学与研究用途的架构复刻实现，与 NVIDIA 无隶属关系；
Cosmos 相关商标归 NVIDIA 所有。
