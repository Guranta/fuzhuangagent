#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infra/docker/docker-compose.yml"
ENV_FILE="$ROOT_DIR/infra/env/.env"
DOMAIN="${DOMAIN:-agent.886668.shop}"
EXPECTED_SERVICES=12
SERVICES=(
  postgres
  redis
  qdrant
  minio
  minio-init
  dify-db
  dify-redis
  dify-api
  dify-worker
  dify-web
  video-service
  caddy
)

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILURES=0

print_ok() {
  printf "%b✅ %s%b\n" "$GREEN" "$1" "$NC"
}

print_warn() {
  printf "%b⚠️  %s%b\n" "$YELLOW" "$1" "$NC"
}

print_fail() {
  printf "%b❌ %s%b\n" "$RED" "$1" "$NC"
}

mark_failure() {
  print_fail "$1"
  FAILURES=$((FAILURES + 1))
}

compose() {
  docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
}

http_code() {
  local url="$1"
  curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 15 "$url" || true
}

detect_base_url() {
  local domain_code
  local local_code

  domain_code="$(http_code "https://$DOMAIN")"
  if [ "$domain_code" != "000" ]; then
    BASE_URL="https://$DOMAIN"
    ACCESS_MODE="server"
    return
  fi

  local_code="$(http_code "http://localhost")"
  if [ "$local_code" != "000" ]; then
    BASE_URL="http://localhost"
    ACCESS_MODE="local"
    return
  fi

  BASE_URL="http://localhost"
  ACCESS_MODE="local"
}

echo "=== Fashion Agent 部署验证 ==="
echo ""

if [ ! -f "$ENV_FILE" ]; then
  echo "缺少环境变量文件: $ENV_FILE"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker 未运行或当前用户无权限访问 Docker。"
  exit 1
fi

detect_base_url
printf "%b目标地址:%b %s (%s 模式)\n\n" "$BLUE" "$NC" "$BASE_URL" "$ACCESS_MODE"

echo "[1/6] 检查容器状态..."
running_services="$(compose ps --services --status running || true)"
running_count=0
for service in "${SERVICES[@]}"; do
  if printf '%s\n' "$running_services" | grep -Fxq "$service"; then
    running_count=$((running_count + 1))
  else
    mark_failure "服务未运行: $service"
  fi
done

if [ "$running_count" -eq "$EXPECTED_SERVICES" ]; then
  print_ok "所有 $EXPECTED_SERVICES/$EXPECTED_SERVICES 个服务均处于运行状态"
else
  mark_failure "运行中的服务数量不足: $running_count/$EXPECTED_SERVICES"
fi
echo ""

echo "[2/6] 检查健康状态..."
for service in "${SERVICES[@]}"; do
  container_id="$(compose ps -q "$service" || true)"
  if [ -z "$container_id" ]; then
    mark_failure "无法找到服务容器: $service"
    continue
  fi

  health_status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$container_id" 2>/dev/null || true)"
  container_status="$(docker inspect --format '{{.State.Status}}' "$container_id" 2>/dev/null || true)"

  case "$health_status" in
    healthy)
      print_ok "$service 健康检查正常"
      ;;
    no-healthcheck)
      if [ "$container_status" = "exited" ] && [ "$service" = "minio-init" ]; then
        exit_code="$(docker inspect --format '{{.State.ExitCode}}' "$container_id" 2>/dev/null || true)"
        if [ "$exit_code" = "0" ]; then
          print_ok "$service 已成功执行完成"
        else
          mark_failure "$service 已退出，退出码: ${exit_code:-unknown}"
        fi
      elif [ "$container_status" = "running" ]; then
        print_warn "$service 未定义 healthcheck，但容器正在运行"
      else
        mark_failure "$service 无 healthcheck 且状态异常: ${container_status:-unknown}"
      fi
      ;;
    starting)
      mark_failure "$service 仍在启动中"
      ;;
    unhealthy)
      mark_failure "$service 健康检查失败"
      ;;
    *)
      if [ "$container_status" = "running" ]; then
        print_warn "$service 健康状态未知，但容器正在运行: ${health_status:-unknown}"
      else
        mark_failure "$service 状态异常: container=${container_status:-unknown}, health=${health_status:-unknown}"
      fi
      ;;
  esac
done
echo ""

echo "[3/6] 检查外部访问..."
external_code="$(http_code "$BASE_URL")"
if [ "$external_code" = "200" ] || [ "$external_code" = "307" ] || [ "$external_code" = "308" ]; then
  print_ok "$BASE_URL 可访问，HTTP $external_code"
else
  mark_failure "$BASE_URL 访问失败，HTTP ${external_code:-000}"
fi
echo ""

echo "[4/6] 检查 Dify Web..."
dify_code="$(http_code "$BASE_URL")"
if [ "$dify_code" = "200" ] || [ "$dify_code" = "307" ]; then
  print_ok "Dify Web 响应正常，HTTP $dify_code"
else
  mark_failure "Dify Web 响应异常，HTTP ${dify_code:-000}"
fi
echo ""

echo "[5/6] 检查视频处理服务..."
video_service_response="$(docker exec fashion-agent-video-service curl -fsS http://localhost:8000/health 2>/dev/null || true)"
video_ready_response="$(docker exec fashion-agent-video-service curl -fsS http://localhost:8000/ready 2>/dev/null || true)"
if [ -n "$video_service_response" ] && [ -n "$video_ready_response" ]; then
  print_ok "Video Service /health: $video_service_response"
  print_ok "Video Service /ready: $video_ready_response"
else
  mark_failure "Video Service 健康端点检查失败"
fi
echo ""

echo "[6/6] 检查 HTTPS 证书..."
if [ "$ACCESS_MODE" = "server" ]; then
  cert_info="$(curl -svI --connect-timeout 5 --max-time 15 "https://$DOMAIN" 2>&1 || true)"
  cert_expire_line="$(printf '%s\n' "$cert_info" | grep 'expire date' || true)"
  if [ -n "$cert_expire_line" ]; then
    print_ok "$cert_expire_line"
  else
    mark_failure "未获取到 HTTPS 证书过期时间"
  fi
else
  print_warn "本地模式跳过 HTTPS 证书检查"
fi
echo ""
echo "=== 验证完成 ==="

if [ "$FAILURES" -gt 0 ]; then
  printf "%b验证失败:%b 共 %d 项关键检查未通过\n" "$RED" "$NC" "$FAILURES"
  exit 1
fi

printf "%b所有关键检查均通过%b\n" "$GREEN" "$NC"
