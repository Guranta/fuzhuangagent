#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

printf "[1/3] preparing env...\n"
if [ ! -f "$ROOT_DIR/infra/env/.env" ]; then
  cp "$ROOT_DIR/infra/env/.env.example" "$ROOT_DIR/infra/env/.env"
fi

printf "[2/3] starting infrastructure...\n"
docker compose -f "$ROOT_DIR/infra/docker/docker-compose.yml" --env-file "$ROOT_DIR/infra/env/.env" up -d

printf "[3/3] starting video service...\n"
cd "$ROOT_DIR/services/video-service"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
