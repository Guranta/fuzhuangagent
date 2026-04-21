# 服装博主智能体APP (Fashion Agent)

为服装带货博主量身定制的AI脚本创作智能体——懂你的货、懂你的风格、懂爆款逻辑。

## 项目结构

```
├── infra/                   # 基础设施配置
│   ├── docker/              # Docker Compose 编排
│   ├── env/                 # 环境变量模板
│   └── nginx/               # 反向代理配置
├── dify/                    # Dify AI编排配置
│   ├── docs/                # Dify使用文档
│   ├── prompts/             # Prompt模板
│   ├── workflow-specs/      # 工作流规格定义
│   ├── datasets/            # 知识库数据集
│   └── evals/               # 评估用例
├── services/                # 微服务
│   └── video-service/       # 视频处理服务
│       ├── app/             # 应用代码
│       ├── tests/           # 测试
│       └── scripts/         # 工具脚本
├── tests/                   # 跨系统集成测试
│   ├── integration/
│   └── fixtures/
└── docs/                    # 项目文档
    ├── architecture/        # 架构设计
    ├── runbooks/            # 运维手册
    └── decisions/           # 技术决策记录
```

## 快速开始

### 前置条件
- Docker & Docker Compose
- Python 3.11+
- DeepSeek API Key

### 启动步骤

```bash
# 1. 配置环境变量
cp infra/env/.env.example infra/env/.env
# 编辑 .env 填入 API Key 等配置

# 2. 启动 Dify 全栈
cd infra/docker
docker compose up -d

# 3. 启动视频处理服务
cd services/video-service
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. 访问 Dify
# http://localhost
```

## 技术栈

| 组件 | 技术选型 |
|------|---------|
| AI编排 | Dify |
| 大模型 | DeepSeek |
| 向量数据库 | Qdrant |
| 关系数据库 | PostgreSQL |
| 缓存 | Redis |
| 对象存储 | MinIO |
| 视频下载 | yt-dlp |
| 语音转录 | faster-whisper |
| 场景切分 | TransNetV2 |
| 视频服务 | FastAPI |
| 部署 | Docker Compose |

## 当前进度

- [x] Wave 0: 仓库骨架 + 数据合约 + 评估fixture + 质量评分卡
- [x] Wave 1: Docker Compose 基础设施启动验证通过（Dify+Qdrant+PostgreSQL+Redis+MinIO）
- [x] Wave 2: Prompt v1 + 数据导入模板 + 基础评估样例
- [x] Wave 3: Dify 脚本生成工作流规格、导入模板、API 调用样例、配置手册
- [x] Wave 4: 视频处理服务（FastAPI + yt-dlp + Whisper + TransNetV2）—— pytest 通过、`/health` 返回 200、`/api/v1/video/process` 错误传播验证通过
- [x] Wave 5: 爆款分析工作流规格、Prompt、API 调用样例与接入说明
- [ ] Wave 6: 健壮性、回归测试、运维细化（后续迭代）

## 已验证的运行证据

| 验证项 | 结果 |
|--------|------|
| `pytest tests/test_app.py` | 1 passed |
| `curl /health` | `{"status":"ok","version":"0.1.0"}` |
| `curl /api/v1/video/process`（无效URL） | 正确返回 400 错误详情 |
| `docker compose config` | 配置解析成功 |
| `docker compose up -d` | 10 容器全部启动，5 healthy |
| Dify Web `localhost:3000` | 307 重定向到安装页（首次启动正确行为） |
| Qdrant `localhost:6333` | 返回空集合列表，正常 |
| MinIO `localhost:9000` | health check 通过 |
| LSP diagnostics | 0 errors, 0 warnings |

## 下一步：在 Dify UI 中完成配置

按照 `docs/runbooks/dify-setup.md` 操作：

1. 访问 `http://localhost:3000` 完成管理员初始化
2. 在 Settings → Model Providers 中配置 DeepSeek API Key
3. 创建两个知识库并导入 `dify/datasets/` 下的 CSV 文件
4. 按 `dify/workflow-specs/script-generation-workflow.md` 创建脚本生成工作流
5. 按 `dify/workflow-specs/viral-analysis-workflow.md` 创建爆款分析工作流
6. 用 `dify/docs/workflow-api-curl.sh` 验证端到端流程
