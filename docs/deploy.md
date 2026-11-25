# deephunch 部署手册

## 一、裸机部署（最低配置即可运行 mock 后端）

```bash
git clone http://data.gitgg.com/<group>/deephunch.git
cd deephunch
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8300
```

浏览器打开 `http://<服务器IP>:8300` 即进入中文控制台。

## 二、Docker 部署

```bash
docker compose up -d --build
```

## 三、接入真实世界模型后端

1. 自行部署推理服务（例如开源 Cosmos-Predict2、或任意扩散模型视频服务），
   暴露 `POST /generate` 接口，入参 `{model, mode, prompt, seed, duration_s}`，
   返回 `{video_url}`。
2. 配置环境变量后重启：

```bash
export DEEPHUNCH_WFM_BACKEND=remote
export DEEPHUNCH_WFM_REMOTE_URL=http://10.0.0.5:9000
export DEEPHUNCH_WFM_REMOTE_TOKEN=<可选>
```

## 四、数据持久化

SQLite 数据库与产物位于 `data/` 目录，容器部署时已通过 volume 挂载；
生产环境建议将 `DEEPHUNCH_DB` 指向 PostgreSQL（修改 `db.py` 连接串即可）。

## 五、生产化建议

- 任务队列：将 `services/worker.py` 线程池替换为 Celery/Arq + GPU 节点
- 护栏：Pre-guard 接内容安全模型（Aegis 类），Post-guard 接视频分类 + 人脸模糊服务
- 对象存储：产物改存 S3/OSS，前端签名直链下载
- 认证：网关层加 SSO/API Key（GitLab OAuth 即可）
