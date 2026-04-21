#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

printf "[1/3] 准备环境变量...\n"
if [ ! -f "$ROOT_DIR/infra/env/.env" ]; then
  cp "$ROOT_DIR/infra/env/.env.example" "$ROOT_DIR/infra/env/.env"
  echo "⚠️  已创建 .env 文件，请编辑填入实际值后重新运行"
  exit 1
fi

printf "[2/3] 启动所有服务（Dify + 视频服务 + Caddy）...\n"
docker compose -f "$ROOT_DIR/infra/docker/docker-compose.yml" --env-file "$ROOT_DIR/infra/env/.env" up -d

printf "[3/3] 等待服务就绪...\n"
sleep 10
docker compose -f "$ROOT_DIR/infra/docker/docker-compose.yml" ps

echo ""
echo "✅ 服务已启动"
echo "   本地访问: http://localhost"
echo "   域名访问: https://${DOMAIN:-agent.886668.shop}"
echo ""
echo "运行验证: ./scripts/verify-deploy.sh"
