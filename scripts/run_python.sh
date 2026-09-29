#!/usr/bin/env bash
set -e

PORT="${PORT:-5050}"
HOST="${HOST:-0.0.0.0}"

echo "=========================================="
echo "    Starting CredentialIQ AI Python API"
echo "=========================================="
echo "Listening on http://${HOST}:${PORT}"
echo "Swagger UI available at http://${HOST}:${PORT}/docs"
echo ""

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

PYTHONPATH=. uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
