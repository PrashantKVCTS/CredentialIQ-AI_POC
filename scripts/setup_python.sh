#!/usr/bin/env bash
set -e

echo "=========================================="
echo "   CredentialIQ AI Python Environment Setup"
echo "=========================================="

# Ensure virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating local virtual environment (.venv)..."
    python3 -m venv .venv
fi
source .venv/bin/activate

echo "Installing required Python dependencies..."
pip install -q -r requirements.txt

echo "Running pytest test suite..."
PYTHONPATH=. pytest tests/

echo ""
echo "Setup complete! Python engine and pytest quality gates passed."
