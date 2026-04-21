# Dify Setup

## 目标

在 Dify UI 中完成脚本生成工作流的最小可用配置。

## 1. 模型提供商

在 Dify 后台 Settings → Model Providers 中：

1. 安装 DeepSeek provider 或使用 OpenAI-compatible provider
2. 填入 DeepSeek API Key
3. 设置 Base URL 为 `https://api.deepseek.com/v1`（如果走 OpenAI 兼容方式）
4. 选择模型 `deepseek-chat`

## 2. 知识库导入

建议建立两个知识库：

1. `products-kb`
2. `historical-scripts-kb`

导入文件：

- `dify/datasets/products_import_template.csv`
- `dify/datasets/historical_scripts_import_template.csv`

建议：

- Chunk 模式：General
- Delimiter：`\n\n`
- Max chunk length：500
- Overlap：50
- Retrieval Top K：5

## 3. 脚本生成工作流节点顺序

1. Start
2. Knowledge Retrieval（products-kb）
3. Knowledge Retrieval（historical-scripts-kb）
4. If/Else（判断 viral_reference 是否为空）
5. LLM（使用 `dify/prompts/script-generation-v1.md`）
6. End

## 4. 输入变量

- `product_name`
- `special_instructions`
- `viral_reference`

## 5. 爆款分析工作流节点顺序

1. Start
2. HTTP Request（调用视频服务 `/api/v1/video/process`）
3. LLM（使用 `dify/prompts/viral-analysis-v1.md`）
4. End

## 6. 发布与 API 调用

发布为 Workflow App 后，使用：

- `dify/docs/workflow-api-example.json`
- `dify/docs/workflow-api-curl.sh`
- `dify/docs/viral-analysis-api-example.json`
- `dify/docs/viral-analysis-api-curl.sh`

调用 `/v1/workflows/run`
