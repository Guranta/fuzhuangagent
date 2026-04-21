# 服务器部署指南

## 服务器要求
- 2 vCPU / 4GB RAM / 20GB SSD
- Ubuntu 22.04+
- 可访问公网的域名与服务器公网 IP

## 前置条件
- 已安装 Docker
- 已安装 Docker Compose

## 部署步骤

### 1. 克隆仓库
```bash
git clone <your-repo-url>
cd 服装智能体
```

### 2. 配置环境变量
```bash
cp infra/env/.env.example infra/env/.env
```

编辑 `infra/env/.env`，至少填写以下内容：
- `DOMAIN`：实际访问域名
- `DEEPSEEK_API_KEY`：DeepSeek API Key
- `POSTGRES_PASSWORD`：PostgreSQL 密码
- `MINIO_SECRET_KEY`：MinIO 密码
- `DIFY_ADMIN_EMAIL` / `DIFY_ADMIN_PASSWORD`：Dify 初始管理员

### 3. 生成 Dify 密钥
```bash
openssl rand -hex 32
```

将输出结果填入 `DIFY_SECRET_KEY`。

### 4. 配置 DNS
为你的域名添加 A 记录，使其指向服务器公网 IP。`DOMAIN` 必须与实际解析域名一致。

### 5. 启动服务
```bash
docker compose -f infra/docker/docker-compose.yml --env-file infra/env/.env up -d
```

### 6. 等待健康检查完成
首次启动通常需要 2-5 分钟，等待 PostgreSQL、Redis、Qdrant、MinIO、Dify、video-service 和 Caddy 全部就绪。

### 7. 验证访问
```bash
curl https://YOUR_DOMAIN
```

## 验证清单
- `docker compose -f infra/docker/docker-compose.yml --env-file infra/env/.env ps`：所有服务为 `Up` / `healthy`
- `curl -I https://DOMAIN`：返回 200
- `curl -I https://DOMAIN/health`：返回 200 或重定向
- 浏览器访问域名时 HTTPS 证书有效

## 首次配置
1. 打开 `https://DOMAIN` 完成 Dify 管理员初始化
2. 在 Dify 中配置 DeepSeek API
3. 创建知识库并导入产品数据
4. 创建或导入工作流

更多配置步骤见 `docs/runbooks/dify-setup.md`。

## 常见问题
- 证书申请失败：检查域名 DNS 是否已生效，且服务器 80 端口已对公网开放
- Dify 无法启动：检查 `DIFY_SECRET_KEY` 是否已设置且长度正确
- 登录或回调地址异常：检查 `DOMAIN` 是否与实际访问域名完全一致
- 视频处理超时：提高 `VIDEO_PROCESS_TIMEOUT` 的值后重启相关服务

## 维护
- 查看日志：`docker compose -f infra/docker/docker-compose.yml --env-file infra/env/.env logs -f [service]`
- 重启服务：`docker compose -f infra/docker/docker-compose.yml --env-file infra/env/.env restart [service]`
- 更新部署：`git pull && docker compose -f infra/docker/docker-compose.yml --env-file infra/env/.env up -d --build`
- 备份卷：
  - `fashion_agent_postgres_data` → PostgreSQL 主库数据
  - `fashion_agent_redis_data` → Redis 数据
  - `fashion_agent_qdrant_data` → Qdrant 向量数据
  - `fashion_agent_minio_data` → MinIO 对象数据
  - `fashion_agent_dify_postgres_data` → Dify PostgreSQL 数据
  - `fashion_agent_dify_redis_data` → Dify Redis 数据
  - `fashion_agent_caddy_data` → Caddy 证书与状态数据
  - `fashion_agent_caddy_config` → Caddy 配置数据

## 端口说明
- 仅 Caddy 对外暴露 80/443
- PostgreSQL、Redis、Qdrant、MinIO、Dify API/Web、video-service 均只在 Docker 内部网络中通信
