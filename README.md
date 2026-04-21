# 服装博主智能体APP (Fashion Agent)

为服装带货博主量身定制的AI脚本创作智能体。

## 核心功能
- 专属个人知识库（产品信息 + 历史脚本风格学习）
- 爆款视频逻辑拆解（下载→转录→结构化分析）
- 按固定四段结构生成带货脚本（钩子→内容→干货→总结）

## 技术栈
| 组件 | 技术选型 |
|------|---------|
| AI 编排 | Dify 0.15.3 |
| 大模型 | DeepSeek |
| 向量数据库 | Qdrant v1.13.4 |
| 反向代理 | Caddy 2.9 (自动 HTTPS) |
| 视频处理 | FastAPI + yt-dlp + Whisper |
| 部署 | Docker Compose |

## 快速开始

### 本地开发
```bash
# 1. 配置环境变量
cp infra/env/.env.example infra/env/.env

# 2. 启动所有服务
docker compose -f infra/docker/docker-compose.yml --env-file infra/env/.env up -d

# 3. 访问
# http://localhost (Dify Web)
```

### 服务器部署
详见 `docs/runbooks/deployment.md`

## 项目结构
```text
├── infra/
│   ├── caddy/               # Caddy 反向代理配置
│   │   └── Caddyfile
│   ├── docker/              # Docker Compose 编排
│   │   └── docker-compose.yml
│   └── env/                 # 环境变量模板
│       └── .env.example
├── dify/                    # Dify 工作流、数据集与说明
├── services/
│   └── video-service/       # 视频处理微服务
│       ├── app/             # FastAPI 应用代码
│       ├── tests/           # 服务测试
│       ├── Dockerfile       # 容器镜像构建
│       └── entrypoint.sh    # 容器启动脚本
├── docs/
│   ├── architecture/
│   ├── decisions/
│   └── runbooks/
│       ├── deployment.md
│       ├── dify-setup.md
│       └── local-setup.md
└── tests/                   # 跨系统集成测试
```

## 部署说明
- 通过 `DOMAIN` 环境变量配置对外域名，默认示例为 `agent.886668.shop`
- 所有业务服务仅加入 Docker 内部网络，只有 Caddy 暴露 80/443
- Caddy 负责反向代理与自动 HTTPS 证书申请

## 首次使用
1. 访问 Dify Web 完成管理员初始化
2. 配置 DeepSeek 模型
3. 创建知识库并导入产品数据
4. 创建工作流

详见 `docs/runbooks/dify-setup.md`
