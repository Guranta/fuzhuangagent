#!/bin/bash
set -e

echo "Starting Fashion Agent Video Service..."
echo "Environment: ${APP_ENV:-production}"
echo "Whisper model: ${WHISPER_MODEL:-base}"

mkdir -p "${VIDEO_DOWNLOAD_DIR:-/tmp/fashion-agent/videos}"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${VIDEO_SERVICE_PORT:-8000}" \
    --workers "${VIDEO_SERVICE_WORKERS:-1}" \
    --log-level "${LOG_LEVEL:-info}" \
    --no-access-log
