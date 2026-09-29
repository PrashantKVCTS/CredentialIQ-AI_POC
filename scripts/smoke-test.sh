#!/usr/bin/env bash
set -e

PORT="${PORT:-5050}"
BASE_URL="http://localhost:${PORT}"

echo "=========================================="
echo "    CredentialIQ AI API Smoke Tests       "
echo "=========================================="

echo "[1/5] Testing GET /health..."
HEALTH_RES=$(curl -s "${BASE_URL}/health")
echo "Health Response: ${HEALTH_RES}"
if ! echo "$HEALTH_RES" | grep -q "Healthy"; then
  echo "ERROR: Health check failed!"
  exit 1
fi

echo -e "\n[2/5] Testing GET /api/system/info..."
INFO_RES=$(curl -s "${BASE_URL}/api/system/info")
echo "System Info Response: ${INFO_RES}"

echo -e "\n[3/5] Testing POST /api/credentialingcases with clean-provider.json..."
CLEAN_RES=$(curl -s -X POST "${BASE_URL}/api/credentialingcases" \
  -H "Content-Type: application/json" \
  -d @"samples/clean-provider.json")
echo "Clean Response: ${CLEAN_RES}"
if ! echo "$CLEAN_RES" | grep -q "Clean"; then
  echo "ERROR: Expected Clean classification!"
  exit 1
fi

echo -e "\n[4/5] Testing POST /api/credentialingcases with exception-provider.json..."
EXC_RES=$(curl -s -X POST "${BASE_URL}/api/credentialingcases" \
  -H "Content-Type: application/json" \
  -d @"samples/exception-provider.json")
echo "Exception Response: ${EXC_RES}"
if ! echo "$EXC_RES" | grep -q "Exception"; then
  echo "ERROR: Expected Exception classification!"
  exit 1
fi

echo -e "\n[5/5] Testing POST /api/credentialingcases with hold-provider.json..."
HOLD_RES=$(curl -s -X POST "${BASE_URL}/api/credentialingcases" \
  -H "Content-Type: application/json" \
  -d @"samples/hold-provider.json")
echo "Hold Response: ${HOLD_RES}"
if ! echo "$HOLD_RES" | grep -q "Hold"; then
  echo "ERROR: Expected Hold classification!"
  exit 1
fi

echo -e "\n=========================================="
echo "   All Smoke Tests Passed Successfully!   "
echo "=========================================="
