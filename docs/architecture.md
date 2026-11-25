# deephunch 平台架构

## 设计目标

对标 NVIDIA Cosmos（arXiv:2501.03575）世界基础模型平台的**架构级一比一复刻**，
为物理 AI（机器人 / 自动驾驶 / 具身智能）提供从数据到模型的全链路平台。

## 总体架构

```
┌────────────────────────────── deephunch 平台 ──────────────────────────────┐
│                                                                            │
│  原始视频 ─▶ dh-curator ─▶ dh-tokenizer ─▶ dh-worldmodel ─▶ dh-posttrain   │
│             (NeMo Curator)  (Cosmos        (Predict/        (NeMo         │
│                              Tokenizer)     Transfer)        微调)         │
│                                                                            │
│              ┌──────────────── dh-guardrails ────────────────┐             │
│              │ Pre-guard（提示词过滤）⇄ Post-guard（输出审核） │             │
│              └────────────────────────────────────────────────┘             │
│                                                                            │
│  dh-registry（模型仓库，对应 NGC 目录）   Web 控制台（中文 SPA）             │
└────────────────────────────────────────────────────────────────────────────┘
```

## 模块说明

### 1. dh-curator 数据策展
五阶段流水线：`split → transcode → filter → caption → embed`
- **split**：镜头边界检测，长视频切为 10s 片段
- **transcode**：统一为 H.264 / 720p / 24fps
- **filter**：分辨率、美观度、运动量三重阈值过滤
- **caption**：VLM 双语打标（训练提示对）
- **embed**：CLIP 风格语义嵌入，支持「雪夜路面」「仓库拥堵」等场景检索

### 2. dh-tokenizer 视觉分词
| 配置 | 模式 | 时间压缩 | 空间压缩 | 供下游 |
|---|---|---|---|---|
| dh-tok-c8x8x8 | 连续 | 8x | 8×8 | 扩散 WFM |
| dh-tok-d8x16x16 | 离散 | 8x | 16×16 | 自回归 WFM |

### 3. dh-worldmodel 世界生成
任务类型：`text2world`、`image2world`、`video2world`、`transfer(sim2real)`。
后端可插拔：默认 `mock`（无 GPU 跑通全流程）；设 `DEEPHUNCH_WFM_BACKEND=remote`
与 `DEEPHUNCH_WFM_REMOTE_URL` 后接任意 HTTP 推理服务（如 Cosmos-Predict2）。

### 4. dh-posttrain 后训练
`dh-predict-lora`（LoRA r=32）/ `dh-predict-sft` 两种预设，产出
适配器工件并注册到模型仓库。

### 5. dh-guardrails 双层护栏
- **Pre-guard**：提示词关键词/内容安全模型拦截
- **Post-guard**：输出视频审核 + 人脸模糊

### 6. dh-registry 模型仓库
predict / transfer / reason 三家族工件注册，版本与许可（dh-open-model-license）管理。

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST/GET | /api/curator/datasets | 数据集管理 |
| POST/GET | /api/curator/jobs | 策展任务 |
| GET/POST | /api/tokenizer/configs · /jobs | Tokenizer |
| POST/GET | /api/worldmodel/jobs | 世界生成（自动过 Pre-guard） |
| POST/GET | /api/posttrain/jobs | 后训练 |
| POST/GET | /api/guardrails/pre · /events | 护栏 |
| GET/POST | /api/registry | 模型仓库 |
