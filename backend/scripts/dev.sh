#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${API_PORT:-9321}"
exec .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port "$PORT"
