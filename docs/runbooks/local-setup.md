# Local Setup

## 目标

在本地跑通两个最小链路：

1. Dify 基础设施可启动
2. 视频处理服务可启动并响应 `/health`

## 前置条件

- 已安装 Docker 与 Docker Compose
- 已安装 Python 3.11+
- 已安装 FFmpeg

## Python 依赖安装

```bash
cd services/video-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 运行视频处理服务

```bash
cd services/video-service
uvicorn app.main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

预期响应：

```json
{"status":"ok","version":"0.1.0"}
```

## 启动基础设施

```bash
cp infra/env/.env.example infra/env/.env
cd infra/docker
docker compose up -d
docker compose ps
```

## 备注

- Dify 的 DeepSeek 配置在 Dify UI 内完成，不需要单独写代码
- 如果 `faster-whisper` 或 `transnetv2-pytorch` 安装失败，可先只验证 `/health` 路由与模块导入
