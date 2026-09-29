# CredentialIQ AI Setup Script for Windows PowerShell
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      CredentialIQ AI Environment Setup   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "Restoring packages..." -ForegroundColor Yellow
dotnet restore CredentialIQ.sln

Write-Host "Building solution in Release configuration..." -ForegroundColor Yellow
dotnet build CredentialIQ.sln --configuration Release

Write-Host "Running automated test suite..." -ForegroundColor Yellow
dotnet test CredentialIQ.sln --configuration Release --no-build

Write-Host "`nSetup complete! All build and test quality gates passed." -ForegroundColor Green
