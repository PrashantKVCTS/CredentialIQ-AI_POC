#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

source .venv/bin/activate

echo "============================================="
echo " Starting CredentialIQ AI FastAPI Web API"
echo "============================================="

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
