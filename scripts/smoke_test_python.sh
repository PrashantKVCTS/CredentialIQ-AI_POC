#!/usr/bin/env bash
set -e

PORT="${PORT:-5050}"
BASE_URL="http://localhost:${PORT}"

echo "=========================================="
echo "    CredentialIQ AI Python API Smoke Tests"
echo "=========================================="

echo "[1/5] Testing GET /health..."
HEALTH_RESP=$(curl -s "${BASE_URL}/health")
echo "Health Response: ${HEALTH_RESP}"
echo "${HEALTH_RESP}" | grep -q "Healthy" || { echo "ERROR: Health check failed!"; exit 1; }

echo ""
echo "[2/5] Testing GET /api/system/info..."
SYS_RESP=$(curl -s "${BASE_URL}/api/system/info")
echo "System Info Response: ${SYS_RESP}"
echo "${SYS_RESP}" | grep -q "CredentialIQ AI" || { echo "ERROR: System info failed!"; exit 1; }

echo ""
echo "[3/5] Testing POST /api/credentialingcases with clean-provider.json..."
CLEAN_RESP=$(curl -s -X POST "${BASE_URL}/api/credentialingcases" -H "Content-Type: application/json" -d @samples/clean-provider.json)
echo "Clean Response: ${CLEAN_RESP}"
echo "${CLEAN_RESP}" | grep -q "Approved" || { echo "ERROR: Expected Approved status!"; exit 1; }

echo ""
echo "[4/5] Testing POST /api/credentialingcases with exception-provider.json..."
EXC_RESP=$(curl -s -X POST "${BASE_URL}/api/credentialingcases" -H "Content-Type: application/json" -d @samples/exception-provider.json)
echo "Exception Response: ${EXC_RESP}"
echo "${EXC_RESP}" | grep -q "CommitteeReview" || { echo "ERROR: Expected CommitteeReview status!"; exit 1; }

echo ""
echo "[5/5] Testing POST /api/credentialingcases with hold-provider.json..."
HOLD_RESP=$(curl -s -X POST "${BASE_URL}/api/credentialingcases" -H "Content-Type: application/json" -d @samples/hold-provider.json)
echo "Hold Response: ${HOLD_RESP}"
echo "${HOLD_RESP}" | grep -q "OnHold" || { echo "ERROR: Expected OnHold status!"; exit 1; }

echo ""
echo "=========================================="
echo "   All Python Smoke Tests Passed Successfully!"
echo "=========================================="
