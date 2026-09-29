#!/usr/bin/env bash
set -e

DOTNET_CMD="/config/.dotnet/dotnet"
if ! command -v "$DOTNET_CMD" &> /dev/null; then
  DOTNET_CMD="dotnet"
fi

PORT="${PORT:-5050}"
export ASPNETCORE_URLS="http://localhost:${PORT}"

echo "Starting CredentialIQ AI Web API on http://localhost:${PORT}..."
echo "Swagger UI available at http://localhost:${PORT}/swagger"

$DOTNET_CMD run --project src/CredentialIQ.Api/CredentialIQ.Api.csproj --no-launch-profile
