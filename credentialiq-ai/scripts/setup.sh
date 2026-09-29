#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================="
echo " Setting up CredentialIQ AI Virtual Environment"
echo "============================================="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment .venv with system site packages..."
    python3 -m venv --system-site-packages .venv
fi

source .venv/bin/activate

echo "Upgrading pip and installing missing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Environment setup complete!"
