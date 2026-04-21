#!/bin/bash
set -e

echo "[dify-api] Running database migrations..."
flask db upgrade 2>&1 || {
  echo "[dify-api] WARNING: Migration failed, attempting to continue..."
}

echo "[dify-api] Starting Dify API..."
exec /bin/bash /entrypoint.sh
