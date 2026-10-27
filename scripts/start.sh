#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
  echo 'Run python3 -m venv .venv and .venv/bin/python -m pip install -r requirements.txt first.'
  exit 1
fi
if [ ! -f frontend/dist/index.html ]; then
  echo 'Build frontend first: cd frontend && npm ci && npm run build'
  exit 1
fi
exec .venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
