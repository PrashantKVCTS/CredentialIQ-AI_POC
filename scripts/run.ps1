# CredentialIQ AI Run Script for Windows PowerShell
$ErrorActionPreference = "Stop"

$port = $env:PORT
if ([string]::IsNullOrWhiteSpace($port)) { $port = "5050" }
$env:ASPNETCORE_URLS = "http://localhost:$port"

Write-Host "Starting CredentialIQ AI Web API on http://localhost:$port..." -ForegroundColor Green
Write-Host "Swagger UI available at http://localhost:$port/swagger" -ForegroundColor Cyan

dotnet run --project src/CredentialIQ.Api/CredentialIQ.Api.csproj --no-launch-profile
