#!/usr/bin/env bash
set -e

DOTNET_CMD="/config/.dotnet/dotnet"
if ! command -v "$DOTNET_CMD" &> /dev/null; then
  DOTNET_CMD="dotnet"
fi

echo "=========================================="
echo "      CredentialIQ AI Environment Setup   "
echo "=========================================="

echo "Restoring packages..."
$DOTNET_CMD restore CredentialIQ.sln

echo "Building solution in Release configuration..."
$DOTNET_CMD build CredentialIQ.sln --configuration Release

echo "Running automated test suite..."
$DOTNET_CMD test CredentialIQ.sln --configuration Release --no-build

echo ""
echo "Setup complete! All build and test quality gates passed."
